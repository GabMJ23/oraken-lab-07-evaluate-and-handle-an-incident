"""Checks for Lab 7, Part B: messages.md. They check that both messages exist and are real messages."""
import pathlib
import re

MESSAGES = pathlib.Path(__file__).resolve().parent.parent / "messages.md"
SECTIONS = ["During the incident", "To users who received a wrong answer"]


def text():
    assert MESSAGES.exists(), "messages.md is missing."
    return re.sub(r"<!--.*?-->", "", MESSAGES.read_text(encoding="utf-8"), flags=re.S)


def section(t, heading):
    m = re.search(rf"^##\s*{re.escape(heading)}\b.*$", t, re.M | re.I)
    assert m, f'messages.md: the heading "## {heading}" is missing. Keep both headings of the template.'
    nxt = re.search(r"^#{1,2}\s", t[m.end():], re.M)
    return t[m.end(): m.end() + nxt.start()] if nxt else t[m.end():]


def sentences(body):
    """Pieces of text ending with . ! or ? that have at least 3 words."""
    parts = re.split(r"(?<=[.!?])\s+", body.strip())
    return [p for p in parts if re.search(r"[.!?]$", p) and len(re.findall(r"\w+", p)) >= 3]


def test_no_todo_left():
    left = text().count("TODO")
    assert left == 0, f"{left} TODO left in messages.md: write both messages."


def test_both_messages_have_at_least_two_sentences():
    t = text()
    for heading in SECTIONS:
        n = len(sentences(section(t, heading)))
        assert n >= 2, (
            f'messages.md, "{heading}": {n} sentence(s). Write at least 2: what is happening, '
            "what is not lost, and what the user should do."
        )
