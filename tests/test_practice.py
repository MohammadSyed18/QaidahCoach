import tempfile, unittest
from pathlib import Path
from qaidahcoach.practice import PracticeStore
from qaidahcoach.review import ReviewBook


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "practice.db"
        self.store = PracticeStore(self.path)
        self.at = "2026-07-01T10:00:00Z"

    def test_restart_feedback_and_idempotent_review_export(self):
        state = self.store.start(["madd"], 2, 1, self.at)
        identifier = state["id"]
        self.assertNotIn("answer", state["next"])
        self.assertNotIn("rule", state["next"])
        for index in range(2):
            state = PracticeStore(self.path).show(identifier)
            exercise = state["next"]["id"]
            answer = "madd" if index == 0 else "iqlab"
            feedback = self.store.answer(identifier, exercise, answer, self.at)
            self.assertEqual(
                feedback, self.store.answer(identifier, exercise, answer, self.at)
            )
            with self.assertRaises(ValueError):
                self.store.answer(identifier, exercise, "other", self.at)
        self.assertTrue(self.store.show(identifier)["complete"])
        book = ReviewBook()
        self.store.export_reviews(book)
        self.store.export_reviews(book)
        self.assertEqual(len(book.attempts), 1)
        self.assertEqual(book.states["madd"].lapses, 1)

    def test_incomplete_quiz_is_not_exported_and_time_is_checked(self):
        state = self.store.start(["madd", "ghunnah"], 3, 1, self.at)
        book = ReviewBook()
        self.assertEqual(self.store.export_reviews(book), 0)
        with self.assertRaises(ValueError):
            self.store.answer(
                state["id"], state["next"]["id"], "madd", "2026-06-01T10:00:00Z"
            )
        with self.assertRaises(KeyError):
            self.store.answer(state["id"], "unknown", "madd", self.at)
