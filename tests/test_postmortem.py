"""Checks for Lab 7, Part B: postmortem.md. They check the format and the blameless tone, not your reasoning.

How the "blameless" check works (it is deliberately simple):
- it fails on a few phrases that point at a person: "fault of", "'s fault", "blame", "blamed",
  "careless", "negligent", "negligence", "sloppy", "incompetent", "human error";
  ("blameless" is fine);
- every "Owner:" must be a role, so it must contain a role word such as team, on-call, lead,
  engineer, support, backend, platform. "Owner: Backend on-call" passes; "Owner: Dave" fails.
A script cannot judge tone. These checks catch the obvious slips; the rest is up to you.
"""
import pathlib
import re

POSTMORTEM = pathlib.Path(__file__).resolve().parent.parent / "postmortem.md"
HEADINGS = ["What happened", "Timeline", "Root cause", "Mitigation", "What was missing", "Actions"]
BLAME = [r"\bfault of\b", r"['’]s fault\b", r"\bblame[sd]?\b", r"\bcareless", r"\bnegligen",
         r"\bsloppy\b", r"\bincompetent", r"\bhuman error\b"]
ROLE_WORDS = ["team", "on-call", "oncall", "on call", "lead", "engineer", "engineering", "manager", "support",
              "ops", "operations", "sre", "backend", "back-end", "frontend", "front-end", "platform", "infra",
              "data", "product", "security", "legal", "qa", "ml", "ai", "devops", "analyst", "editor", "editorial",
              "content", "owner", "rotation", "squad", "reviewer", "counsel", "compliance", "designer", "writer"]
DATE = re.compile(r"\b20\d\d-[01]\d-[0-3]\d\b")
OWNER = re.compile(r"owner\s*:\s*([^.;|\n]+)", re.I)


def text():
    assert POSTMORTEM.exists(), "postmortem.md is missing."
    return re.sub(r"<!--.*?-->", "", POSTMORTEM.read_text(encoding="utf-8"), flags=re.S)


def section(t, heading):
    m = re.search(rf"^#{{2,3}}\s*{re.escape(heading)}\b.*$", t, re.M | re.I)
    assert m, f'postmortem.md: the heading "## {heading}" is missing. Keep the six headings of the template.'
    nxt = re.search(r"^#{1,3}\s", t[m.end():], re.M)
    return t[m.end(): m.end() + nxt.start()] if nxt else t[m.end():]


def action_lines(t):
    lines = section(t, "Actions").splitlines()
    return [ln for ln in lines if re.match(r"\s*([-*+]|\d+[.)])\s", ln)]


def test_all_headings_present():
    t = text()
    for heading in HEADINGS:
        section(t, heading)


def test_no_todo_left():
    t = text()
    left = t.count("TODO")
    assert left == 0, f"{left} TODO left in postmortem.md: fill every section."
    for heading in HEADINGS:
        words = len(re.findall(r"\w+", section(t, heading)))
        assert words >= 15, f'postmortem.md: the "{heading}" section is too short ({words} words). Say more.'


def test_timeline_starts_with_the_reports():
    tl = section(text(), "Timeline")
    assert re.search(r"\b(2:05|14:05)\b", tl), "Timeline: put the first user reports at 2:05 pm on March 12."


def test_root_cause_names_the_cache_and_the_version():
    rc = section(text(), "Root cause").lower()
    assert "cache" in rc and "version" in rc, (
        "Root cause: explain what the cache did with the text's version (date). Both words should appear."
    )


def test_at_least_three_actions_with_date_and_owner():
    complete = [ln for ln in action_lines(text()) if DATE.search(ln) and OWNER.search(ln)]
    assert len(complete) >= 3, (
        f"{len(complete)} complete action(s) found in the Actions section. Write at least 3 lines like:\n"
        "  - Include the version date in the cache key. Owner: Backend team. Due: 2026-03-19"
    )


def test_owners_are_roles_not_people():
    for ln in action_lines(text()):
        for owner in OWNER.findall(ln):
            words = re.findall(r"[a-z]+(?:-[a-z]+)?", owner.lower())
            joined = " ".join(words)
            ok = any(w in words for w in ROLE_WORDS) or any(" " in r and r in joined for r in ROLE_WORDS)
            assert ok, (
                f'Owner "{owner.strip()}" does not look like a role. In a blameless postmortem the owner is a role '
                '(like "Backend on-call" or "Support lead"), never a person.'
            )


def test_no_blame():
    t = text()
    for pattern in BLAME:
        m = re.search(pattern, t, re.I)
        assert not m, (
            f'postmortem.md says "{m.group(0)}". A blameless postmortem describes what the system lacked, '
            "not who is at fault. Rewrite that sentence around the process or the code."
        )
