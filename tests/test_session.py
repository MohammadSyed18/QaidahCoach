import unittest
from qaidahcoach.session import mixed_session,check_answer
from qaidahcoach.mastery import mastery,next_rule
class SessionTests(unittest.TestCase):
 def test_mixed_session_rotates_rules(self):self.assertEqual([x.rule for x in mixed_session(["madd","qalqalah"],4,2).exercises],["madd","qalqalah","madd","qalqalah"])
 def test_answer_feedback_includes_explanation(self):
  item=mixed_session(["ikhfa"],1).exercises[0];result=check_answer(item,"ikhfa");self.assertTrue(result["correct"]);self.assertTrue(result["explanation"])
 def test_mastery_selects_weak_rule(self):
  report=mastery([{"rule":"madd","correct":True}]*3+[{"rule":"iqlab","correct":False}]*3);self.assertEqual(next_rule(report),"iqlab")
