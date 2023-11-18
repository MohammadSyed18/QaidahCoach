import unittest
from qaidahcoach.exercises import generate
class ExerciseTests(unittest.TestCase):
 def test_generation_is_deterministic(self):self.assertEqual(generate("madd",5,42),generate("madd",5,42))
 def test_all_rules_have_explanation_and_transliteration(self):
  for rule in ["madd","qalqalah","ghunnah","ikhfa","idgham","iqlab"]:
   item=generate(rule,1)[0];self.assertTrue(item.explanation);self.assertTrue(item.transliteration)
 def test_invalid_rule(self):self.assertRaises(ValueError,generate,"unknown")
