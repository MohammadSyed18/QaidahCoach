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
