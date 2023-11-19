import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from .practice import PracticeStore
from .review import ReviewBook


def main():
    parser = argparse.ArgumentParser(
        description="Saved Qaidah rule-identification practice"
    )
    parser.add_argument("--database", default="data/practice.sqlite3")
    parser.add_argument("--at", default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("rules", nargs="+")
    start.add_argument("--count", type=int, default=6)
    start.add_argument("--seed", type=int, default=1)
    commands.add_parser("show").add_argument("session")
    answer = commands.add_parser("answer")
    answer.add_argument("session")
    answer.add_argument("exercise")
    answer.add_argument("answer")
    commands.add_parser("export-reviews").add_argument("ledger", type=Path)
    args = parser.parse_args()
    at = args.at or datetime.now(timezone.utc).isoformat()
    try:
        store = PracticeStore(args.database)
        if args.command == "start":
            result = store.start(args.rules, args.count, args.seed, at)
        elif args.command == "show":
            result = store.show(args.session)
        elif args.command == "answer":
            result = store.answer(args.session, args.exercise, args.answer, at)
        else:
            book = ReviewBook.load(args.ledger)
            result = {"rule_reviews": store.export_reviews(book)}
            book.save(args.ledger)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
