# Lab 7: Evaluate, and handle an incident

**Part 5 · Lessons 14 and 15 · about 2 hours · automatically checked**

## Goals

- Build a small evaluation set and score an assistant in a way that another person can rerun and get close results.
- Write a blameless postmortem for a realistic incident, and the messages users read while it happens and after.

## Before you start

You need Python 3.12 and Git. Create your own copy of this lab (**Use this template** on GitHub), clone it, then:

```bash
python -m venv .venv
# macOS / Linux: source .venv/bin/activate      Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q          # most checks fail at first: that is expected
```

Rules for every lab: one Git repository, one commit per step, your answers in `REPORT.md`, and no secret in Git.

**Set your budget first.** Before you run anything, write in `REPORT.md` (A0) how many dollars you allow yourself for this lab: the assistant's calls and the judge's calls. You will compare it with the real cost at the end. With the offline assistant and a free chat for the judge, $0 is a valid budget.

## Part A: Evaluate

1. **Pick an assistant and write 10 questions.** Choose one of:
   - your mini-RAG from Lab 3, or your capstone assistant;
   - a general assistant with a connector (you collect its answers by hand);
   - `fake_assistant.py`, "Holiday Helper": a small offline assistant about US federal holidays (5 U.S.C. 6103). Pick it if you have no assistant at hand, or to practice first. Try it: `python fake_assistant.py`.

   Write your questions in `eval/questions.json`, in the lesson 14 format. The file already holds two examples:
   ```json
   { "id": "q01", "question": "When is Memorial Day?",
     "must_contain": ["last Monday in May"], "must_not": ["May 30"], "off_topic": false }
   ```
   - `must_contain`: the short phrases a good answer must have (a fact, a date, the source it must cite).
   - `must_not`: phrases that make the answer wrong (an outdated fact, a common confusion). Every question needs at least one.
   - At least **2 off-topic questions** that the assistant must politely refuse or redirect: `"off_topic": true` and a `"refusal_marker"`, a phrase (or a list of phrases) that shows the refusal, like `["only help with", "can't help"]`. For these, `must_contain` can hold the redirect you expect, or stay empty.

   Keep each phrase short: the script checks it word for word (case does not matter). "last Monday in May" works; a whole sentence almost never matches.

2. **Score each answer, 3 runs per question.** A model does not give the same answer twice, so one run proves nothing. In `evaluate.py`, write:
   - `score(answer, item)`: **2** if everything expected is there and nothing forbidden; **1** if incomplete (some expected phrases, not all); **0** if wrong (none of them) or if the answer contains anything from `must_not`. A `must_not` always wins, even over a complete answer. Matching ignores case. For an off-topic item: no refusal marker gives 0; a refusal gives 2, or 1 if the expected redirect (`must_contain`) is missing.
   - `aggregate(runs)`: `runs` maps each question id to its list of scores, like `{"q01": [2, 2, 1]}`. Return the mean and the spread (best minus worst) of each question, the overall percentage (points earned over points possible), and the largest spread. The docstring shows the exact shape.

   Then run the evaluation:
   ```bash
   python evaluate.py --assistant fake              # the offline Holiday Helper
   python evaluate.py --assistant rag:answer        # your own: module rag.py, function answer(question) -> str
   python evaluate.py --answers eval/answers.json   # answers you collected by hand, 3 per question
   ```
   For your own assistant, `evaluate.py` imports the module from this folder: copy your Lab 3 code here, or write a three-line wrapper file whose function takes a question and returns the answer text. Keep its API key in an environment variable or a `.env` file, never in Git. For a general assistant, ask each question in 3 new conversations and paste the answers into `eval/answers.json` (`eval/answers.example.json` shows the format). Each run prints a table and saves every answer and score to `eval/results.json`: commit it, so another pair can check your scores.

3. **Automate part of the scoring with a judge.** Your `score()` checks that the expected phrases are present. It cannot see an error worded in a new way, or a correct answer worded differently. A second model can, if you give it a clear rubric. Write that rubric in `eval/judge_prompt.md`: what the judge receives, what 0, 1 and 2 mean, and the exact JSON it must reply with, starting with `{"score": ...}`. Use the placeholders `{question}`, `{answer}`, `{must_contain}` and `{must_not}`, then run:
   ```bash
   python evaluate.py --assistant fake --judge-sheet 10
   ```
   It writes `eval/judge_sheet.md`: ten ready-to-paste prompts, each with your script's score. Paste each one into another model (a free chat is fine), note its score, and compare (A4). JSON matters: a script can read the judge's score later, without a human.

4. **Record the real cost.** Add up what the assistant and the judge actually cost (your provider's usage page, or tokens times price as in lesson 3). Compare it with your budget (A5).

Write your answers in `REPORT.md`.

## Part B: An incident

The scenario. Your team runs an assistant that answers questions about a state's overtime rules and cites the section it relies on. On **March 1, 2026**, Section 4.2 of the rule (the rule is fictional) was amended, and its paragraph (c) was removed. On **March 12 at 2:05 pm**, several users report that answers still cite paragraph (c). The investigation shows that legal texts are cached for 30 days, without taking their version date into account.

1. **Write the postmortem** in `postmortem.md`, in the lesson 14 format. Keep the six headings of the template: What happened, Timeline, Root cause, Mitigation, What was missing, Actions. Write each action on one line, with an owner and a due date:
   ```markdown
   - Include the text's version date in the cache key. Owner: Backend team. Due: 2026-03-19
   ```
   The postmortem is **blameless**: it names what the system lacked, never who is at fault. Owners are roles ("Backend on-call", "Support lead"), never people. Fill in what the scenario does not say (when the cache was filled, when the fix went out), as long as it stays consistent.

   The checks are simple on purpose. They look for the six headings, the 2:05 pm reports in the timeline, the cache and the version in the root cause, and at least 3 actions with a `YYYY-MM-DD` date and an `Owner:` that contains a role word (team, on-call, lead, engineer, support...). They fail on phrases that point at a person ("fault of", "blame", "careless", "human error"). A script cannot judge tone: these checks catch the obvious slips, and the rest is up to you. The comment at the top of `tests/test_postmortem.py` lists every rule.

2. **Write the two messages** in `messages.md` (lesson 15): the banner users see during the incident, and the email sent after the fix to users who received a wrong answer. Each one says, in plain words, what is happening, what is not lost, and what to do. No jargon: a user does not know what a cache is.

## Deliverable and success criteria

- `evaluate.py`, `eval/questions.json`, `eval/results.json`, `eval/judge_prompt.md`, `postmortem.md`, `messages.md` and `REPORT.md` committed.
- **Success:** `pytest -q` is all green. Another pair can rerun your evaluation from your repository and get close results. Your postmortem names no culprit.
- Each time you push, GitHub runs the same checks (the **Actions** tab shows a green or red mark). The checks never call a model: they test `score()` and `aggregate()` on hand-made answers and on the offline assistant.

**Going further:** add a question about a recently amended text to your evaluation set: it is the test your postmortem asks for. Does your assistant pass it on all 3 runs? With the Holiday Helper, ask how many federal holidays there are: Juneteenth was added in 2021, and about one run in three still says 10.

Stuck? Open `HINTS.md`: three hints, from gentle to almost the answer.
