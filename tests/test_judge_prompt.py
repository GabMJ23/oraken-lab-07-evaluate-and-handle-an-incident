"""Checks that eval/judge_prompt.md is a usable judge prompt. It does not grade its quality."""
import pathlib
import re

JUDGE = pathlib.Path(__file__).resolve().parent.parent / "eval" / "judge_prompt.md"


def text():
    assert JUDGE.exists(), "eval/judge_prompt.md is missing."
    return re.sub(r"<!--.*?-->", "", JUDGE.read_text(encoding="utf-8"), flags=re.S)


def test_judge_prompt_is_written():
    t = text()
    assert "TODO" not in t, "eval/judge_prompt.md still says TODO: write your judge prompt."
    assert len(re.findall(r"\w+", t)) >= 60, "eval/judge_prompt.md is too short to guide a judge (60 words or more)."


def test_judge_prompt_has_a_0_1_2_rubric():
    t = text()
    for s in "012":
        assert re.search(rf"(?<![\w.]){s}(?![\w.])", t), f"The rubric must say what a score of {s} means (0, 1 and 2)."
    assert re.search(r"\bscore", t, re.I), "Say that the judge gives a score."


def test_judge_prompt_asks_for_json():
    t = text()
    assert re.search(r"\bjson\b", t, re.I), "Ask the judge to reply in JSON, so a script can read its score."
    assert re.search(r"\{\s*\"score\"", t), 'Show the exact JSON shape you expect, starting with {"score": ...}.'
