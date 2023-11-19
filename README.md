# qaidahcoach

practice tools for foundational Arabic reading

Python: mixed sessions, answer checking, rule explanations, mastery
TypeScript: spaced review, daily accuracy, streaks, difficult items

```sh
python3.12 -m unittest discover -s tests -v
python3.12 -m qaidahcoach.cli madd --seed 7
npm install
npm test
npm run build
```

these are limited instructional examples. they don't cover every contextual recitation difference or replace practice with a qualified teacher.

## Implementation details

`qaidahcoach.progress` provides posterior mastery estimates, uncertainty intervals, and balanced follow-up practice plans. The planner prioritizes weaker rules while avoiding immediate repetition.

## Persistent rule review

[review.py](qaidahcoach/review.py) adds a local spaced-review ledger with 0–5 quality ratings, bounded ease and intervals, lapse recovery, due-rule selection, and reproducible exercises. Attempt IDs make retries idempotent and conflicting reuse is rejected. UTC-aware timestamps prevent accidental reordering. Atomic writes preserve a saved ledger if writing is interrupted; loading replays recorded inputs and checks computed results.

```sh
python -m qaidahcoach.review_cli --at 2026-10-22T12:00:00Z due
python -m qaidahcoach.review_cli --at 2026-10-22T12:00:00Z record attempt-1 madd 4
python -m qaidahcoach.review_cli --at 2026-10-23T12:00:00Z practice --seed 7
```

The default ledger is `data/reviews.json`, excluded from Git. This is a single-writer local store. Ratings are manually supplied; this code does not perform speech recognition or grade recorded recitation. Tests cover interval growth, lapses, retry conflicts, out-of-order reviews, persistence integrity, and due-rule selection.
