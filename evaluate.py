"""Lab 7, Part A: score an assistant, reproducibly.

Run it:   python evaluate.py --assistant fake
          python evaluate.py --assistant my_module:my_function
          python evaluate.py --answers eval/answers.json
Test it:  pytest -q

Your job: write score() and aggregate(). Everything else (loading the
questions, calling the assistant 3 times, printing the table, saving
eval/results.json) is already written.
"""
import argparse
import importlib
import json
import pathlib
import re
import sys

RUNS = 3  # each question is asked 3 times: one run proves nothing
QUESTIONS = "eval/questions.json"
RESULTS = "eval/results.json"
JUDGE_PROMPT = "eval/judge_prompt.md"
JUDGE_SHEET = "eval/judge_sheet.md"


def normalize(text):
    """Lowercase and collapse whitespace, so matching ignores case and line breaks."""
    return re.sub(r"\s+", " ", (text or "")).strip().casefold()


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def score(answer, item):
    """Score one answer against one question of the evaluation set.

    Returns 2 (everything expected is there, nothing forbidden),
            1 (incomplete: some, not all, of what is expected),
            0 (wrong: nothing expected, or anything from "must_not").

    Matching is case-insensitive. A "must_not" match always gives 0.
    For an off-topic item ("off_topic": true), the answer must contain one of
    the "refusal_marker" strings: no refusal gives 0; a refusal without the
    expected redirect ("must_contain", often empty) gives 1.
    """
    # TODO (Part A, step 2): write this function. HINTS.md can help.
    raise NotImplementedError("score() is not written yet: see Part A, step 2 of the README.")


def aggregate(runs):
    """Summarize the scores of several runs.

    `runs` maps a question id to the list of its scores, one per run:
        {"q01": [2, 2, 1], "q02": [0, 1, 0], ...}

    Returns:
        {
          "per_question": {"q01": {"mean": 1.667, "spread": 1}, ...},
          "overall_pct": 58.3,   # all points earned / all points possible * 100
          "max_spread": 1,       # the largest spread of any question
        }
    The spread of a question is its best score minus its worst score.
    Do not round: the table rounds for display.
    """
    # TODO (Part A, step 2): write this function. HINTS.md can help.
    raise NotImplementedError("aggregate() is not written yet: see Part A, step 2 of the README.")


# ---------------------------------------------------------------------------
# Everything below is plumbing: you do not need to change it.
# ---------------------------------------------------------------------------

def load_questions(path=QUESTIONS):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def load_assistant(name):
    """'fake' gives the offline Holiday Helper; 'module:function' imports your own.

    Your function must take a question (str) and return the answer (str).
    """
    if name == "fake":
        from fake_assistant import FakeAssistant
        return FakeAssistant()
    if ":" not in name:
        raise SystemExit("--assistant must be 'fake' or 'module:function', for example 'rag:answer'.")
    module, function = name.split(":", 1)
    sys.path.insert(0, str(pathlib.Path.cwd()))
    return getattr(importlib.import_module(module), function)


def run_eval(items, assistant, runs=RUNS):
    """Ask every question `runs` times. Returns {id: [{"answer": ..., "score": ...}, ...]}."""
    results = {}
    for item in items:
        results[item["id"]] = []
        for _ in range(runs):
            answer = assistant(item["question"])
            results[item["id"]].append({"answer": answer, "score": score(answer, item)})
    return results


def score_answers(items, answers):
    """Score answers you collected by hand: {id: [answer_run1, answer_run2, ...]}."""
    results = {}
    for item in items:
        collected = answers.get(item["id"], [])
        results[item["id"]] = [{"answer": a, "score": score(a, item)} for a in collected]
    return results


def scores_of(results):
    return {qid: [r["score"] for r in rows] for qid, rows in results.items() if rows}


def table(items, results, summary):
    runs = max(len(rows) for rows in results.values())
    head = f"{'id':<5} {'question':<46}" + "".join(f" run{i + 1}" for i in range(runs)) + "   mean spread"
    lines = [head, "-" * len(head)]
    for item in items:
        rows = results.get(item["id"], [])
        if not rows:
            continue
        q = item["question"] if len(item["question"]) <= 46 else item["question"][:43] + "..."
        cells = "".join(f" {r['score']:>4}" for r in rows) + "     " * (runs - len(rows))
        stats = summary["per_question"][item["id"]]
        lines.append(f"{item['id']:<5} {q:<46}{cells}   {stats['mean']:.2f} {stats['spread']:>6}")
    lines.append("-" * len(head))
    lines.append(f"Overall: {summary['overall_pct']:.1f}%   largest spread across runs: {summary['max_spread']}")
    return "\n".join(lines)


def fill_judge_prompt(template, item, answer):
    """Fill the placeholders {question}, {answer}, {must_contain}, {must_not} of your judge prompt."""
    values = {
        "{question}": item["question"],
        "{answer}": str(answer or ""),
        "{must_contain}": json.dumps(as_list(item.get("must_contain"))),
        "{must_not}": json.dumps(as_list(item.get("must_not"))),
    }
    # One pass, so an answer that happens to contain "{question}" is left as it is.
    return re.sub(r"\{(question|answer|must_contain|must_not)\}", lambda m: values[m.group(0)], template)


def write_judge_sheet(items, results, n, path=JUDGE_SHEET, prompt_path=JUDGE_PROMPT):
    """Write the first `n` answers as ready-to-paste judge prompts, with your own score kept aside."""
    template = pathlib.Path(prompt_path).read_text(encoding="utf-8")
    template = re.sub(r"<!--.*?-->", "", template, flags=re.S)  # drop the guide comments
    if "{answer}" not in template:
        print(f"Warning: {prompt_path} has no {{answer}} placeholder; the answers are appended at the end.")
        template += "\n\nQuestion: {question}\n\nAnswer to grade:\n{answer}\n"
    by_id = {item["id"]: item for item in items}
    parts, count = ["# Judge sheet\n\nPaste each prompt into another model. Note its score next to yours.\n"], 0
    for qid, rows in results.items():
        for run, row in enumerate(rows, 1):
            if count == n:
                break
            count += 1
            parts.append(f"## {count}. {qid}, run {run} (your script's score: {row['score']}, judge's score: ...)\n")
            parts.append("```text\n" + fill_judge_prompt(template, by_id[qid], row["answer"]).strip() + "\n```\n")
    pathlib.Path(path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Judge sheet with {count} answers written to {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Score an assistant on eval/questions.json.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--assistant", help="'fake' or 'module:function'")
    source.add_argument("--answers", help="JSON file of answers you collected: {id: [run1, run2, run3]}")
    parser.add_argument("--questions", default=QUESTIONS)
    parser.add_argument("--runs", type=int, default=RUNS)
    parser.add_argument("--out", default=RESULTS)
    parser.add_argument("--judge-sheet", type=int, metavar="N", help="also write N answers as judge prompts")
    args = parser.parse_args(argv)

    items = load_questions(args.questions)
    if args.assistant:
        results = run_eval(items, load_assistant(args.assistant), runs=args.runs)
    else:
        answers = json.loads(pathlib.Path(args.answers).read_text(encoding="utf-8"))
        results = score_answers(items, answers)
    summary = aggregate(scores_of(results))
    print(table(items, results, summary))
    pathlib.Path(args.out).write_text(
        json.dumps({"results": results, "summary": summary}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Every answer and score saved to {args.out}")
    if args.judge_sheet:
        write_judge_sheet(items, results, args.judge_sheet)


if __name__ == "__main__":
    main()
