"""Checks that REPORT.md is filled in. It does not grade your reasoning: it makes sure nothing is left blank."""
import pathlib
import re

REPORT = pathlib.Path(__file__).resolve().parent.parent / "REPORT.md"


def section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


def test_report_exists():
    assert REPORT.exists(), "REPORT.md is missing."


def test_required_answers_filled():
    text = REPORT.read_text(encoding="utf-8")
    required = section(text, "## Part A", "**Going further")
    left = required.count("TODO")
    assert left == 0, f"{left} required answer(s) still say TODO in REPORT.md (Parts A and B)."


def test_a2_gives_the_overall_score():
    text = REPORT.read_text(encoding="utf-8")
    a2 = section(text, "**A2.**", "**A3.**")
    assert re.search(r"\d+(\.\d+)?\s*%", a2), "A2: give the overall score as a percentage, like 86.7%."


def test_budget_and_real_cost_are_in_dollars():
    text = REPORT.read_text(encoding="utf-8")
    a0 = section(text, "**A0.**", "**A1.**")
    a5 = section(text, "**A5.**", "**A6.**")
    assert re.search(r"\$\s?\d", a0), "A0: write your budget in dollars before you start, like $2.00."
    assert re.search(r"\$\s?\d", a5), "A5: write the real cost in dollars, like $0.37 (or $0 if it was free)."
