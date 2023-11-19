"""Local review commands: no microphone or speech-recognition claims."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from .review import ReviewBook
from .exercises import to_dicts


def main():
    parser = argparse.ArgumentParser(description="Qaidah rule review ledger")
    parser.add_argument("--ledger", type=Path, default=Path("data/reviews.json"))
    parser.add_argument("--at", default=None, help="ISO timestamp with time zone")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("due")
    practice = commands.add_parser("practice")
    practice.add_argument("--seed", type=int, default=1)
    record = commands.add_parser("record")
    record.add_argument("id")
    record.add_argument("rule")
    record.add_argument("quality", type=int)
    args = parser.parse_args()
    at = args.at or datetime.now(timezone.utc).isoformat()
    try:
        book = ReviewBook.load(args.ledger)
        if args.command == "record":
            result = asdict(book.record(args.id, args.rule, args.quality, at))
            book.save(args.ledger)
        elif args.command == "practice":
            result = to_dicts(book.exercises(at, seed=args.seed))
        else:
            result = [asdict(state) for state in book.due(at)]
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
