"""Durable local quizzes with answer retries, feedback, and review-ledger export."""

from contextlib import contextmanager
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from .session import mixed_session, check_answer
from .exercises import Exercise, RULES
from .review import parse_time


class PracticeStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript(
                """PRAGMA journal_mode=WAL;
              CREATE TABLE IF NOT EXISTS practice_sessions(
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, exercises TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS practice_answers(
                session_id TEXT NOT NULL, exercise_id TEXT NOT NULL, answer TEXT NOT NULL,
                at TEXT NOT NULL, correct INTEGER NOT NULL, PRIMARY KEY(session_id,exercise_id),
                FOREIGN KEY(session_id) REFERENCES practice_sessions(id));"""
            )

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise

    def start(self, rules, count, seed, at):
        if type(count) is not int or not 1 <= count <= 50 or type(seed) is not int:
            raise ValueError("practice needs 1..50 questions and an integer seed")
        created = parse_time(at).isoformat()
        plan = mixed_session(rules, count, seed)
        identifier = str(uuid4())
        with self.transaction() as db:
            db.execute(
                "INSERT INTO practice_sessions VALUES(?,?,?)",
                (
                    identifier,
                    created,
                    json.dumps(
                        [asdict(item) for item in plan.exercises], ensure_ascii=False
                    ),
                ),
            )
        return self.show(identifier)

    def _session(self, db, identifier):
        row = db.execute(
            "SELECT * FROM practice_sessions WHERE id=?", (identifier,)
        ).fetchone()
        if row is None:
            raise KeyError("practice session not found")
        return row, json.loads(row["exercises"])

    def show(self, identifier):
        with self.connection() as db:
            row, exercises = self._session(db, identifier)
            answers = {
                item["exercise_id"]: dict(item)
                for item in db.execute(
                    "SELECT * FROM practice_answers WHERE session_id=?", (identifier,)
                )
            }
        remaining = [item for item in exercises if item["id"] not in answers]
        current = None
        if remaining:
            current = {
                key: value
                for key, value in remaining[0].items()
                if key not in {"rule", "answer", "explanation"}
            }
            current["choices"] = sorted(RULES)
        correct = sum(item["correct"] for item in answers.values())
        return {
            "id": identifier,
            "created_at": row["created_at"],
            "total": len(exercises),
            "answered": len(answers),
            "correct": correct,
            "complete": not remaining,
            "next": current,
            "accuracy": correct / len(answers) if answers else None,
        }

    def answer(self, identifier, exercise_id, answer, at):
        if not isinstance(answer, str) or not answer.strip() or len(answer) > 100:
            raise ValueError("answer must contain 1..100 characters")
        answer = answer.strip().lower()
        timestamp = parse_time(at).isoformat()
        with self.transaction() as db:
            row, exercises = self._session(db, identifier)
            if parse_time(timestamp) < parse_time(row["created_at"]):
                raise ValueError("answer precedes session")
            exercise = next(
                (item for item in exercises if item["id"] == exercise_id), None
            )
            if exercise is None:
                raise KeyError("exercise not in this session")
            previous = db.execute(
                "SELECT * FROM practice_answers WHERE session_id=? AND exercise_id=?",
                (identifier, exercise_id),
            ).fetchone()
            feedback = check_answer(Exercise(**exercise), answer)
            if previous:
                if previous["answer"] != answer:
                    raise ValueError("exercise already answered differently")
                return feedback
            latest = db.execute(
                "SELECT max(at) FROM practice_answers WHERE session_id=?", (identifier,)
            ).fetchone()[0]
            if latest and timestamp < latest:
                raise ValueError("answer times must be monotonic")
            db.execute(
                "INSERT INTO practice_answers VALUES(?,?,?,?,?)",
                (identifier, exercise_id, answer, timestamp, int(feedback["correct"])),
            )
            return feedback

    def export_reviews(self, book):
        """Only completed quizzes contribute; deterministic IDs make repeated export safe."""
        with self.connection() as db:
            rows = db.execute(
                "SELECT id,created_at FROM practice_sessions ORDER BY created_at,id"
            ).fetchall()
            staged = []
            for row in rows:
                _, exercises = self._session(db, row["id"])
                answers = {
                    item["exercise_id"]: dict(item)
                    for item in db.execute(
                        "SELECT * FROM practice_answers WHERE session_id=?",
                        (row["id"],),
                    )
                }
                if len(answers) != len(exercises):
                    continue
                at = max(item["at"] for item in answers.values())
                groups = {}
                for exercise in exercises:
                    values = groups.setdefault(exercise["rule"], [])
                    values.append(answers[exercise["id"]]["correct"])
                for rule, values in groups.items():
                    rate = sum(values) / len(values)
                    quality = 5 if rate >= 0.9 else 3 if rate >= 0.7 else 1
                    staged.append((at, f"practice:{row['id']}:{rule}", rule, quality))
        # Stage the destination too: one invalid timestamp cannot partially advance it.
        from copy import deepcopy

        candidate = deepcopy(book)
        for at, identifier, rule, quality in sorted(staged):
            candidate.record(identifier, rule, quality, at)
        book.states, book.attempts = candidate.states, candidate.attempts
        return len(staged)
