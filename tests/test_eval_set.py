"""Checks that eval/questions.json follows the lesson 14 format. Run with: pytest -q"""
import json
import pathlib

import pytest

QUESTIONS = pathlib.Path(__file__).resolve().parent.parent / "eval" / "questions.json"


def load():
    assert QUESTIONS.exists(), "eval/questions.json is missing."
    try:
        items = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"eval/questions.json is not valid JSON (line {e.lineno}): {e.msg}. A missing comma is the usual cause.")
    assert isinstance(items, list), "eval/questions.json must be a JSON list of questions: [ {...}, {...} ]."
    return items


def strings(value):
    """True if value is a non-empty list of non-empty strings."""
    return isinstance(value, list) and len(value) > 0 and all(isinstance(s, str) and s.strip() for s in value)


def test_at_least_ten_questions():
    items = load()
    assert len(items) >= 10, f"The evaluation set has {len(items)} question(s): write at least 10."


def test_at_least_two_off_topic_questions():
    off = [i for i in load() if isinstance(i, dict) and i.get("off_topic") is True]
    assert len(off) >= 2, (
        f"{len(off)} off-topic question(s) found: add at least 2, with \"off_topic\": true, "
        "that the assistant should politely refuse or redirect."
    )


def test_ids_and_questions():
    items = load()
    ids = []
    for n, item in enumerate(items, 1):
        assert isinstance(item, dict), f"Item {n} is not a JSON object {{...}}."
        assert isinstance(item.get("id"), str) and item["id"].strip(), f"Item {n} needs an \"id\", like \"q{n:02d}\"."
        assert isinstance(item.get("question"), str) and item["question"].strip(), f"{item['id']}: \"question\" is empty."
        ids.append(item["id"])
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicates, f"Each id must be unique. Duplicated: {duplicates}."


def test_every_item_has_expectations():
    for item in load():
        qid = item.get("id", "?")
        assert strings(item.get("must_not")), (
            f"{qid}: \"must_not\" must be a non-empty list of strings: what would make this answer wrong?"
        )
        assert isinstance(item.get("off_topic", False), bool), f"{qid}: \"off_topic\" must be true or false."
        if item.get("off_topic"):
            marker = item.get("refusal_marker")
            ok = (isinstance(marker, str) and marker.strip()) or strings(marker)
            assert ok, (
                f"{qid} is off-topic: add a \"refusal_marker\" (a string, or a list of strings) that shows a polite "
                "refusal, like \"only help with\"."
            )
            assert isinstance(item.get("must_contain", []), list), f"{qid}: \"must_contain\" must be a list (it can be empty here)."
        else:
            assert strings(item.get("must_contain")), (
                f"{qid}: \"must_contain\" must be a non-empty list of strings: what must a good answer say?"
            )
