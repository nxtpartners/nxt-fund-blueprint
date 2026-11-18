"""Questions printed as text, so assistants without an options tool show them the same way every time."""
from __future__ import annotations

import re
from string import ascii_uppercase
from typing import Any, Dict, List

from . import constants as c
from . import wording as w

_HINT = re.compile(r"\s*" + w.ASK_MULTI_HINT + r"[^.?]*[.?]?", re.IGNORECASE)


class AskError(ValueError):
    """The --ask request is not a list of questions this renderer can show."""


def render_questions(request: Dict[str, Any]) -> str:
    """One message: section line, questions with lettered options, any open question, and how to reply."""
    questions = _questions(request)
    open_text = str(request.get(c.ASK_OPEN) or "").strip()
    numbered = len(questions) + (1 if open_text else 0) > 1
    blocks = [_section(request[c.ASK_SECTION])] if request.get(c.ASK_SECTION) else []
    for index, question in enumerate(questions):
        blocks.append(_question(question, index + 1 if numbered else 0))
    if open_text:
        blocks.append(f"{len(questions) + 1}. **{open_text}**" if numbered else f"**{open_text}**")
    blocks.append(_reply_line(questions, bool(open_text), numbered))
    return "\n\n".join(blocks)


def _questions(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(request, dict):
        raise AskError("send a JSON object with a questions list")
    questions = request.get(c.ASK_QUESTIONS)
    if not isinstance(questions, list) or not 1 <= len(questions) <= c.ASK_MAX_QUESTIONS:
        raise AskError(f"questions must hold 1 to {c.ASK_MAX_QUESTIONS} questions")
    for question in questions:
        options = question.get(c.ASK_OPTIONS) if isinstance(question, dict) else None
        if not isinstance(question, dict) or not str(question.get(c.ASK_TEXT) or "").strip():
            raise AskError("every question needs its text")
        if not isinstance(options, list) or not 2 <= len(options) <= c.ASK_MAX_OPTIONS:
            raise AskError(f"every question needs 2 to {c.ASK_MAX_OPTIONS} options")
        if not all(isinstance(option, dict) and str(option.get(c.ASK_LABEL) or "").strip() for option in options):
            raise AskError("every option needs its label")
    return questions


def _section(section: Dict[str, Any]) -> str:
    try:
        return w.ASK_SECTION_LINE.format(
            number=int(section[c.ASK_SECTION_NUMBER]), count=int(section[c.ASK_SECTION_COUNT]), title=section[c.ASK_SECTION_TITLE]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise AskError("section needs number, of, and title") from error


def _question(question: Dict[str, Any], number: int) -> str:
    text = _HINT.sub("", str(question[c.ASK_TEXT])).strip()
    line = f"**{text}**"
    if question.get(c.ASK_MULTI):
        line += f" `{w.ASK_MULTI_HINT}`"
    if number:
        line = f"{number}. {line}"
    options = [_option(ascii_uppercase[i], option) for i, option in enumerate(question[c.ASK_OPTIONS])]
    return "\n".join([line, ""] + options)


def _option(letter: str, option: Dict[str, Any]) -> str:
    description = str(option.get(c.ASK_DESCRIPTION) or "").strip()
    label = str(option[c.ASK_LABEL]).strip()
    if description:
        return w.ASK_OPTION_DESCRIBED.format(letter=letter, label=label, description=description)
    return w.ASK_OPTION_LINE.format(letter=letter, label=label)


def _reply_line(questions: List[Dict[str, Any]], has_open: bool, numbered: bool) -> str:
    """The example shows a reply that fits these questions: '+' only where several answers are allowed."""
    parts = []
    for index, question in enumerate(questions):
        count = len(question[c.ASK_OPTIONS])
        first = index % count
        letters = {first}
        if question.get(c.ASK_MULTI):
            letters.add((first + 2) % count if count > 2 else (first + 1) % count)
        picks = "+".join(ascii_uppercase[i] for i in sorted(letters))
        parts.append(f"{index + 1}{picks}" if numbered else picks)
    if has_open:
        parts.append(f"{len(questions) + 1}: {w.ASK_OPEN_EXAMPLE}")
    line = w.ASK_REPLY.format(example=", ".join(parts))
    if any(question.get(c.ASK_SKIPPABLE, True) for question in questions):
        line += w.ASK_REPLY_SKIP
    return line
