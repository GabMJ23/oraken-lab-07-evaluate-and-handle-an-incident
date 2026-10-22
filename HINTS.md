# Lab 7 hints

Read one hint at a time.

<details>
<summary>Hint 1: in which order should score() check things?</summary>

Think of the rules as a funnel, and check the strongest one first:

1. An empty answer is a 0.
2. Anything from `must_not` in the answer is a 0, whatever else it says. Check it **before** counting the good phrases, otherwise a complete but wrong answer slips through with a 2.
3. Off-topic item: no refusal marker means it answered when it should have refused, so 0.
4. Then count how many `must_contain` phrases are present: all of them is a 2, some is a 1, none is a 0.

For case-insensitive matching, lowercase both sides before comparing. `normalize()` at the top of `evaluate.py` does it for you, and also turns line breaks into spaces.

</details>

<details>
<summary>Hint 2: score(), almost written</summary>

`refusal_marker` can be a string or a list: `as_list()` turns both into a list.

```python
text = normalize(answer)
if not text:
    return 0
if any(normalize(bad) in text for bad in as_list(item.get("must_not"))):
    return 0
expected = [normalize(e) for e in as_list(item.get("must_contain"))]
found = sum(1 for e in expected if e in text)
if item.get("off_topic"):
    refused = any(normalize(m) in text for m in as_list(item.get("refusal_marker")))
    # no refusal: 0. A refusal: 2 if every expected redirect is there, else 1.
    ...
# normal question: all found -> 2, some found -> 1, none -> 0
...
```

</details>

<details>
<summary>Hint 3: aggregate(), and the postmortem checks</summary>

For each question id: `mean = sum(scores) / len(scores)`, `spread = max(scores) - min(scores)`. Keep two running totals: points earned (`sum(scores)`) and points possible (`2 * len(scores)`). At the end, `overall_pct = 100 * earned / possible`, and `max_spread` is the largest spread you stored. Return the three keys `per_question`, `overall_pct` and `max_spread`.

If a postmortem check fails, read its message: it quotes the line or the phrase it did not accept. A complete action line looks like this:

```markdown
- Add a question on a recently amended section to the evaluation set. Owner: AI evaluation lead. Due: 2026-03-26
```

The root cause is not "someone forgot": it is that the cache kept legal texts for 30 days and its key ignored the text's version date.

</details>
