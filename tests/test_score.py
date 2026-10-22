"""Automated checks for Lab 7, Part A: score() and aggregate(). Run with: pytest -q"""
import pathlib

import pytest

import evaluate

MEMORIAL = {
    "id": "q01",
    "question": "When is Memorial Day?",
    "must_contain": ["last Monday in May", "6103"],
    "must_not": ["May 30"],
    "off_topic": False,
}
LASAGNA = {
    "id": "q09",
    "question": "Can you give me a lasagna recipe?",
    "must_contain": ["federal holidays"],
    "must_not": ["preheat", "oven"],
    "off_topic": True,
    "refusal_marker": ["only help with", "can't help"],
}
TAXES = {
    "id": "q10",
    "question": "Can you help me file my taxes?",
    "must_contain": [],
    "must_not": ["Form 1040"],
    "off_topic": True,
    "refusal_marker": "only help with",
}


def check(answer, item, expected, why):
    got = evaluate.score(answer, item)
    assert isinstance(got, int) and not isinstance(got, bool), f"score() must return an int (0, 1 or 2), not {got!r}."
    assert got == expected, f"score() returned {got} instead of {expected}: {why}\n  answer: {answer!r}"


# --- score(): normal questions -------------------------------------------

def test_complete_answer_scores_2():
    check("Memorial Day is the last Monday in May. Source: 5 U.S.C. 6103(a).", MEMORIAL, 2,
          "every expected element is there and nothing forbidden.")


def test_incomplete_answer_scores_1():
    check("Memorial Day is the last Monday in May.", MEMORIAL, 1,
          "one expected element (the 6103 source) is missing: the answer is incomplete.")


def test_wrong_answer_scores_0():
    check("Memorial Day is in June.", MEMORIAL, 0, "none of the expected elements is there.")


def test_empty_answer_scores_0():
    check("", MEMORIAL, 0, "an empty answer is wrong.")


def test_matching_ignores_case():
    check("MEMORIAL DAY IS THE LAST MONDAY IN MAY (5 U.S.C. 6103).", MEMORIAL, 2,
          "matching must be case-insensitive: 'LAST MONDAY IN MAY' counts as 'last Monday in May'.")


def test_must_not_dominates():
    check("It is the last Monday in May (5 U.S.C. 6103), which used to be May 30.", MEMORIAL, 0,
          "the answer contains a 'must_not' element (May 30): that gives 0, even if everything else is there.")


def test_must_not_ignores_case_too():
    check("Last Monday in May, 6103. Formerly MAY 30.", MEMORIAL, 0,
          "'MAY 30' is a 'must_not' element, whatever its case.")


# --- score(): off-topic questions ----------------------------------------

def test_off_topic_refusal_with_redirect_scores_2():
    check("Sorry, I can only help with questions about US federal holidays.", LASAGNA, 2,
          "an off-topic question that is politely refused (and redirected) is a success.")


def test_off_topic_any_refusal_marker_counts():
    check("I can't help with recipes, only with federal holidays.", LASAGNA, 2,
          "'refusal_marker' is a list: any one of its markers shows a refusal.")


def test_off_topic_refusal_marker_can_be_a_string():
    check("Sorry, I can ONLY HELP WITH holidays.", TAXES, 2,
          "'refusal_marker' can be a single string, and matching ignores case.")


def test_off_topic_answered_scores_0():
    check("Sure! Boil the pasta, layer it with sauce and cheese. Federal holidays are a great time to cook.",
          LASAGNA, 0, "the assistant answered an off-topic question instead of refusing: that is a 0.")


def test_off_topic_refusal_without_redirect_scores_1():
    check("Sorry, I can only help with that kind of thing.", LASAGNA, 1,
          "the assistant refused but did not redirect ('federal holidays' is missing): incomplete.")


def test_off_topic_refusal_with_must_not_scores_0():
    check("I can only help with federal holidays, but preheat the oven to 375F.", LASAGNA, 0,
          "a 'must_not' element (oven) gives 0, even when the answer also refuses.")


# --- aggregate() ---------------------------------------------------------

def test_aggregate_mean_spread_and_overall():
    result = evaluate.aggregate({"q01": [2, 2, 2], "q02": [2, 1, 0], "q03": [0, 0, 0]})
    pq = result["per_question"]
    assert set(pq) == {"q01", "q02", "q03"}, "per_question must have one entry per question id."
    assert pq["q01"]["mean"] == pytest.approx(2.0), "q01 scored 2, 2, 2: its mean is 2."
    assert pq["q02"]["mean"] == pytest.approx(1.0), "q02 scored 2, 1, 0: its mean is 1."
    assert pq["q01"]["spread"] == 0, "q01 scored 2, 2, 2: the spread (best minus worst) is 0."
    assert pq["q02"]["spread"] == 2, "q02 scored 2, 1, 0: the spread (best minus worst) is 2."
    assert result["overall_pct"] == pytest.approx(50.0), (
        "overall_pct is all points earned divided by all points possible, times 100: (6 + 3 + 0) / 18 * 100 = 50."
    )
    assert result["max_spread"] == 2, "max_spread is the largest spread of any question (here 2)."


def test_aggregate_perfect_and_uneven_runs():
    result = evaluate.aggregate({"a": [2, 2, 2], "b": [2, 2, 1]})
    assert result["overall_pct"] == pytest.approx(100 * 11 / 12), "11 points out of 12 possible is 91.67%."
    assert result["per_question"]["b"]["mean"] == pytest.approx(5 / 3), "b scored 2, 2, 1: its mean is 1.67."
    assert result["max_spread"] == 1


# --- the whole evaluation, offline ---------------------------------------

def test_three_runs_are_kept():
    assert evaluate.RUNS >= 3, "Keep RUNS at 3 (or more): a single run hides how much answers vary."


HOLIDAY_SET = [
    MEMORIAL,
    {"id": "q04", "question": "How many federal holidays are there?", "must_contain": ["11", "Juneteenth"],
     "must_not": ["10 federal holidays"]},
    {"id": "q08", "question": "When is Veterans Day?", "must_contain": ["November 11"],
     "must_not": ["fourth Monday in October"]},
    LASAGNA,
    TAXES,
]


def test_fake_assistant_evaluation_is_reproducible():
    first = evaluate.run_eval(HOLIDAY_SET, evaluate.load_assistant("fake"))
    second = evaluate.run_eval(HOLIDAY_SET, evaluate.load_assistant("fake"))
    scores = evaluate.scores_of(first)
    assert scores == evaluate.scores_of(second), "Two evaluations of the same assistant should give the same scores."
    assert all(len(s) == 3 for s in scores.values()), "Each question must be asked 3 times."
    assert scores["q09"] == [2, 2, 2] and scores["q10"] == [2, 2, 2], (
        "The fake assistant always refuses the lasagna and tax questions politely: they should score 2 on every run."
    )
    assert 0 in scores["q04"], "The fake assistant once says '10 federal holidays' (a 'must_not'): that run is a 0."
    assert 1 in scores["q01"], "The fake assistant once forgets its source (6103): that run is a 1."
    summary = evaluate.aggregate(scores)
    assert summary == evaluate.aggregate(evaluate.scores_of(second))
    assert 0 < summary["overall_pct"] < 100


def test_your_questions_run_against_the_fake_assistant():
    path = pathlib.Path(__file__).resolve().parent.parent / "eval" / "questions.json"
    items = evaluate.load_questions(path)
    results = evaluate.run_eval(items, evaluate.load_assistant("fake"))
    summary = evaluate.aggregate(evaluate.scores_of(results))
    assert 0 <= summary["overall_pct"] <= 100
