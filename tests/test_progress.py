import unittest
from qaidahcoach.progress import progress_report, practice_plan


class Progress(unittest.TestCase):
    def test_uncertainty_contracts_with_more_attempts(self):
        small = progress_report([{"rule": "madd", "correct": True}])["madd"]
        large = progress_report([{"rule": "madd", "correct": True}] * 20)["madd"]
        self.assertGreater(large["interval"][0], small["interval"][0])

    def test_plan_does_not_repeat_a_rule_back_to_back(self):
        plan = practice_plan([], 30)
        self.assertEqual(len(plan), 30)
        self.assertTrue(all(a != b for a, b in zip(plan, plan[1:])))

    def test_strings_are_not_counted_as_correct(self):
        with self.assertRaises(ValueError):
            progress_report([{"rule": "madd", "correct": "false"}])
