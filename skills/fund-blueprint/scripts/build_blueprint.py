#!/usr/bin/env python3
"""Print the question flow, or turn validated answers into the blueprint."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import datetime as dt
import json
from pathlib import Path

from blueprint.data import Library
from blueprint.render import render_blueprint, render_email, render_summary
from blueprint.scoring import score_answers
from blueprint.validate import AnswerError, parse_answers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-flow", action="store_true", help="Print the questions and options as JSON")
    parser.add_argument("--answers", help="Path to the answers JSON")
    parser.add_argument("--output", help="Path for the blueprint HTML")
    args = parser.parse_args()

    library = Library()
    if args.print_flow:
        print(json.dumps(library.flow(), ensure_ascii=False))
        return 0
    if not args.answers or not args.output:
        parser.error("use --print-flow, or both --answers and --output")

    try:
        with open(args.answers, encoding="utf-8") as handle:
            raw = json.load(handle)
        answers = parse_answers(library, raw)
    except (OSError, ValueError, RecursionError) as error:
        print(f"ANSWER ERROR: {error}", file=sys.stderr)
        return 2

    plan = score_answers(library, answers)
    try:
        Path(args.output).write_text(render_blueprint(answers, plan, library, dt.date.today()), encoding="utf-8")
    except OSError as error:
        print(f"OUTPUT ERROR: could not write the report to {args.output}: {error}", file=sys.stderr)
        return 3
    print(f"BLUEPRINT WRITTEN: {args.output}\n")
    print(render_summary(answers, plan, library))
    print("\nEMAIL DRAFT (show only if the user asks for it):\n")
    print(render_email(answers, plan, library))
    return 0


if __name__ == "__main__":
    sys.exit(main())
