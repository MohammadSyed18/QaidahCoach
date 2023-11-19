"""Persistent, idempotent spaced review for individual reading rules."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile

from .exercises import RULES, generate


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("review times must include a time zone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ReviewState:
    rule: str
    repetitions: int = 0
    lapses: int = 0
    interval_days: int = 0
    ease: float = 2.5
    due_at: str | None = None
    last_reviewed_at: str | None = None


def advance(state: ReviewState, quality: int, at: str) -> ReviewState:
    if state.rule not in RULES or type(quality) is not int or not 0 <= quality <= 5:
        raise ValueError("quality must be 0..5 and rule must be known")
    timestamp = parse_time(at)
    if state.last_reviewed_at and timestamp < parse_time(state.last_reviewed_at):
        raise ValueError("reviews cannot precede earlier attempts")
    ease = max(
        1.3, min(3.5, state.ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )
    if quality < 3:
        repetitions, interval, lapses = 0, 1, state.lapses + 1
    else:
        repetitions = state.repetitions + 1
        interval = (
            1
            if repetitions == 1
            else 6 if repetitions == 2 else max(1, round(state.interval_days * ease))
        )
        interval = min(interval, 365)
        lapses = state.lapses
    return ReviewState(
        state.rule,
        repetitions,
        lapses,
        interval,
        round(ease, 4),
        (timestamp + timedelta(days=interval)).isoformat(),
        timestamp.isoformat(),
    )


class ReviewBook:
    """Single-writer local review ledger; duplicate request IDs never advance twice."""

    def __init__(self):
        self.states = {rule: ReviewState(rule) for rule in sorted(RULES)}
        self.attempts: dict[str, dict] = {}

    def record(self, identifier: str, rule: str, quality: int, at: str) -> ReviewState:
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or len(identifier) > 200
        ):
            raise ValueError("attempt id required")
        if type(quality) is not int or not 0 <= quality <= 5:
            raise ValueError("quality must be an integer from 0 to 5")
        if rule not in self.states:
            raise ValueError("unknown rule")
        payload = {"rule": rule, "quality": quality, "at": parse_time(at).isoformat()}
        if identifier in self.attempts:
            if self.attempts[identifier]["input"] != payload:
                raise ValueError("attempt ID reused with different content")
            return ReviewState(**self.attempts[identifier]["result"])
        updated = advance(self.states[rule], quality, at)
        self.states[rule] = updated
        self.attempts[identifier] = {"input": payload, "result": asdict(updated)}
        return updated

    def due(self, at: str, limit: int = 6) -> list[ReviewState]:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be 1..100")
        now = parse_time(at)
        return sorted(
            (
                state
                for state in self.states.values()
                if state.due_at is None or parse_time(state.due_at) <= now
            ),
            key=lambda state: (state.due_at or "", -state.lapses, state.rule),
        )[:limit]

    def exercises(self, at: str, *, per_rule: int = 2, seed: int = 1):
        if type(per_rule) is not int or not 1 <= per_rule <= 20:
            raise ValueError("per_rule must be 1..20")
        return [
            exercise
            for index, state in enumerate(self.due(at))
            for exercise in generate(state.rule, per_rule, seed + index)
        ]

    def save(self, path: Path) -> None:
        """Atomic replacement protects a saved ledger from an interrupted write."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(
            {"version": 1, "attempts": self.attempts},
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", dir=path.parent, delete=False, encoding="utf8"
            ) as handle:
                temporary = Path(handle.name)
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @classmethod
    def load(cls, path: Path):
        book = cls()
        if not Path(path).exists():
            return book
        data = json.loads(Path(path).read_text())
        if data.get("version") != 1 or not isinstance(data.get("attempts"), dict):
            raise ValueError("unsupported review ledger")
        # Replay inputs rather than trusting persisted computed state.
        for identifier, attempt in data["attempts"].items():
            raw = attempt["input"]
            result = book.record(identifier, raw["rule"], raw["quality"], raw["at"])
            if asdict(result) != attempt["result"]:
                raise ValueError("review ledger result does not match its inputs")
        return book
