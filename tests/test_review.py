import unittest
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from qaidahcoach.review import ReviewBook, ReviewState, advance


class ReviewTests(unittest.TestCase):
    def test_intervals_and_lapse_recovery(self):
        first = advance(ReviewState("madd"), 5, "2026-01-01T00:00:00Z")
        second = advance(first, 5, "2026-01-02T00:00:00Z")
        third = advance(second, 5, "2026-01-08T00:00:00Z")
        self.assertEqual((first.interval_days, second.interval_days), (1, 6))
        self.assertGreater(third.interval_days, second.interval_days)
        failed = advance(third, 1, "2026-02-01T00:00:00Z")
        self.assertEqual(
            (failed.repetitions, failed.interval_days, failed.lapses), (0, 1, 1)
        )

    def test_attempt_idempotency_and_conflicts(self):
        book = ReviewBook()
        first = book.record("a", "madd", 4, "2026-01-01T00:00:00Z")
        book.record("b", "madd", 5, "2026-01-02T00:00:00Z")
        self.assertEqual(book.record("a", "madd", 4, "2026-01-01T00:00:00Z"), first)
        with self.assertRaises(ValueError):
            book.record("a", "madd", 1, "2026-01-01T00:00:00Z")
        with self.assertRaises(ValueError):
            book.record("c", "madd", True, "2026-01-03T00:00:00Z")
        with self.assertRaises(ValueError):
            book.record("d", "madd", 4, "2025-01-01T00:00:00Z")

    def test_due_rules_and_disk_replay(self):
        book = ReviewBook()
        book.record("a", "madd", 4, "2026-01-01T00:00:00Z")
        self.assertNotIn(
            "madd", [item.rule for item in book.due("2026-01-01T10:00:00Z")]
        )
        self.assertIn("madd", [item.rule for item in book.due("2026-01-03T10:00:00Z")])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reviews.json"
            book.save(path)
            loaded = ReviewBook.load(path)
            self.assertEqual(loaded.states, book.states)
            self.assertEqual(
                loaded.exercises("2026-01-03T00:00:00Z"),
                book.exercises("2026-01-03T00:00:00Z"),
            )
            text = path.read_text().replace('"interval_days": 1', '"interval_days": 99')
            path.write_text(text)
            with self.assertRaises(ValueError):
                ReviewBook.load(path)

    def test_naive_time_is_rejected(self):
        with self.assertRaises(ValueError):
            ReviewBook().due("2026-01-01")
