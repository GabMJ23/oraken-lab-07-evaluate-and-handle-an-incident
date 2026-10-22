"""Lab 7: a small, deterministic assistant to evaluate offline.

"Holiday Helper" answers questions about US federal holidays (5 U.S.C. 6103).
It needs no network and no API key. It behaves a bit like a real model:

- most of the time it gives a complete answer with its source;
- sometimes it forgets the source, or a part of the answer (incomplete);
- for one question it sometimes gives an outdated fact (wrong);
- it politely refuses anything that is not about federal holidays.

Its "randomness" is seeded by the question and the run number, so the
same evaluation always gives the same answers, on every machine.
You do not need to change this file.
"""
import random

SOURCE = "Source: 5 U.S.C. 6103(a)."
REFUSAL = (
    "Sorry, I can only help with questions about US federal holidays. "
    "For anything else, please use a general assistant or search engine."
)

# (keywords, official name, date rule). Juneteenth comes before Independence Day
# because its official name contains "Independence Day".
HOLIDAYS = [
    (("new year",), "New Year's Day", "January 1"),
    (("martin luther king", "mlk"), "Birthday of Martin Luther King, Jr.", "the third Monday in January"),
    (("washington", "presidents"), "Washington's Birthday", "the third Monday in February"),
    (("memorial",), "Memorial Day", "the last Monday in May"),
    (("juneteenth",), "Juneteenth National Independence Day", "June 19"),
    (("independence day", "fourth of july", "july 4"), "Independence Day", "July 4"),
    (("labor day",), "Labor Day", "the first Monday in September"),
    (("columbus", "indigenous"), "Columbus Day", "the second Monday in October"),
    (("veterans",), "Veterans Day", "November 11"),
    (("thanksgiving",), "Thanksgiving Day", "the fourth Thursday in November"),
    (("christmas",), "Christmas Day", "December 25"),
]
NOT_FEDERAL = ["easter", "good friday", "halloween", "valentine", "st. patrick", "mother's day", "black friday"]
ON_TOPIC_WORDS = ["holiday", "federal", "observed", "day off", "weekend", "saturday", "sunday"]


class FakeAssistant:
    """Call it like a function: answer = assistant(question).

    It counts how many times it has seen each question, so the 1st, 2nd and
    3rd runs of the same question can differ, but always in the same way.
    """

    def __init__(self):
        self.seen = {}

    def __call__(self, question):
        run = self.seen.get(question, 0)
        self.seen[question] = run + 1
        rng = random.Random(f"{question}|{run}")
        return answer(question, rng)


def answer(question, rng):
    q = question.lower()
    forget_source = rng.random() < 0.3

    def cite(text):
        return text if forget_source else f"{text} {SOURCE}"

    if "how many" in q and ("holiday" in q or "federal" in q):
        if rng.random() < 0.34:
            return "There are 10 federal holidays."  # outdated: true before 2021
        return cite("There are 11 permanent federal holidays. The most recent one, Juneteenth, was added in 2021.")

    if any(w in q for w in ("saturday", "sunday", "weekend", "observed")):
        text = "When a federal holiday falls on a Saturday, most federal employees get the Friday before off."
        if rng.random() >= 0.25:
            text += " When it falls on a Sunday, they get the Monday after off."
        return text + ("" if forget_source else " Source: 5 U.S.C. 6103(b) and Executive Order 11582.")

    for word in NOT_FEDERAL:
        if word in q:
            name = word.title()
            return cite(f"No. {name} is not a federal holiday: it is not on the list of federal holidays.")

    for keywords, name, rule in HOLIDAYS:
        if any(k in q for k in keywords):
            return cite(f"{name} is a federal holiday, observed on {rule}.")

    if any(w in q for w in ON_TOPIC_WORDS):
        return "I am not sure. The official list of federal holidays is in 5 U.S.C. 6103(a)."
    return REFUSAL


if __name__ == "__main__":
    bot = FakeAssistant()
    for question in ["When is Memorial Day?", "How many federal holidays are there?", "Give me a lasagna recipe."]:
        print(question, "->", bot(question))
