"""Evidence-weighted rule progress and balanced follow-up practice."""

from collections import defaultdict
from math import sqrt
from .exercises import RULES


def progress_report(attempts):
    grouped = defaultdict(list)
    for attempt in attempts:
        rule = attempt["rule"]
        correct = attempt["correct"]
        if rule not in RULES or type(correct) is not bool:
            raise ValueError("invalid attempt")
        grouped[rule].append(correct)
    result = {}
    for rule, values in grouped.items():
        n = len(values)
        success = sum(values)
        p = success / n
        z = 1.96
        denom = 1 + z * z / n
        center = (p + z * z / (2 * n)) / denom
        radius = z * sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
        result[rule] = {
            "attempts": n,
            "correct": success,
            "posterior_mean": (success + 1) / (n + 2),
            "interval": (max(0, center - radius), min(1, center + radius)),
            "recent_accuracy": sum(values[-5:]) / len(values[-5:]),
        }
    return result


def practice_plan(attempts, count=12):
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 100:
        raise ValueError("count must be 1..100")
    report = progress_report(attempts)
    rules = sorted(RULES)
    used = defaultdict(int)
    plan = []
    for _ in range(count):

        def priority(rule):
            state = report.get(
                rule, {"posterior_mean": 0.5, "recent_accuracy": 0.5, "attempts": 0}
            )
            need = (
                1
                - state["posterior_mean"]
                + 0.5 * (1 - state["recent_accuracy"])
                + 1 / (state["attempts"] + 2)
            )
            return need / (used[rule] + 1)

        candidates = [r for r in rules if not plan or r != plan[-1]] or rules
        chosen = max(candidates, key=lambda r: (priority(r), r))
        used[chosen] += 1
        plan.append(chosen)
    return plan
