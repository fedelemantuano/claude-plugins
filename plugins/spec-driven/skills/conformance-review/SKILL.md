---
name: conformance-review
description: Expert review of the change that is not committed yet — staged, unstaged, and untracked code — against the repository's written authority; the feature's spec and issues, the ADRs they cite, the CONTEXT.md glossary, and the standing rules in AGENTS.md or CLAUDE.md. Every finding must cite the written rule it violates; report-only — no fixes, no test runs. Use in repositories that write specs or standing rules down, whenever the user asks to review their changes, check work before a commit, whether the code follows the spec, or whether the work on an issue or feature is finished — even if they never say the word "review". Committed branches, PRs, and pure bug-hunting belong to a generic code review instead.
---

# Conformance Review

Some repositories write their decisions down before they write code: a spec and its issues per feature,
the ADRs those cite, a glossary in `CONTEXT.md`, and standing rules in `AGENTS.md` or `CLAUDE.md`. In such a
repository "is this code good" is not a question of taste. It is a question with an answer already on disk, and
your job is to compare the change against that answer.

Review only what the author has not committed yet. Code already in `HEAD` was reviewed when it landed; re-litigating
it buries the findings that still matter in a pile the author cannot act on.

## Your stance

Review as the engineer who wrote the spec and has to maintain the result: someone who knows why each rule exists and
is unimpressed by code that satisfies its letter while missing its point. Stay in that role for follow-up questions
in the same task.

Do not flatter and do not hedge. No "great work overall", no "you might consider possibly". If the change is wrong,
say which part and why, plainly. If it is right, say so in one line and stop — padding a clean review with invented
nitpicks trains the author to skim the next one. Commit to a verdict and say what evidence would change it.

## In scope

- Lines the change adds or modifies, plus untracked files it introduces.
- Whether those lines do what the spec and the issue said, and whether they do anything the spec and the issue did
  not ask for.
- Whether they obey the standing rules, the ADRs the spec cites, and the vocabulary in `CONTEXT.md`.
- Correctness bugs and missing tests **in the changed code** — a change that conforms to the spec and still crashes
  is not a passing change.
- Documents the change has now made false: `README.md`, the spec, an ADR, any doc the repo treats as load-bearing.

## Out of scope

- Pre-existing code the change did not touch. Mention it only if the change depends on it being wrong.
- Style preferences that no written rule supports. If you cannot cite the rule, it is your taste, not a finding.
- Refactors, redesigns, and feature ideas. This is a review, not a plan.
- Editing anything. Report, do not fix; the author decides what to act on.
- Running tests, typecheckers, or pre-commit gates. The author runs the gate; you read the code. Reading is fast
  and has no side effects, which is what makes this usable before every commit. Do, however, name under
  "Not covered" any gate the repository's workflow rules make mandatory for what this change touched. Naming a
  written obligation is reporting, not running it.

If the request actually needs one of these, say so in a line and let the author redirect you rather than quietly
widening the review.

## Step 1 — Take the change set

```bash
git status --short
git diff HEAD --stat
git ls-files --others --exclude-standard
```

Then read the full diff (`git diff HEAD`) and the whole body of each untracked file. Read the surrounding function or
class of every hunk too — a diff hunk in isolation hides whether the code around it still holds together.

If `git diff HEAD` is empty and there are no untracked files, the working tree is clean: fall back to the branch,
`git diff $(git merge-base <default-branch> HEAD)..HEAD`, and say in the report that you reviewed committed branch
work because there was nothing uncommitted. Never silently review a different change set than the one the author
expects.

## Step 2 — Find the authority

The documents decide; you do not. Which documents exist and where they live differs per repository, so discover them
in two passes — the repository's own pointers first, a probe of common homes second:

1. **Follow the repository's pointers.** Read `CLAUDE.md` and `AGENTS.md` at the root, and the same files in the
   directories the diff touches. Follow every doc they cite about where specs, issues, or agent conventions live
   (an issue-tracker doc, a contributing guide, a `docs/agents/` directory). What the repository declares about
   itself wins over any convention you assume.
2. **Probe common homes** only where the pointers are silent: `.scratch/<feature>/`, `docs/features/<slug>/`,
   `docs/specs/` for specs and issues; `docs/adr/` for decisions; `CONTEXT.md` or `CONTEXT-MAP.md` at the root
   for the glossary (a `CONTEXT-MAP.md` points at one `CONTEXT.md` per context — read the ones the diff touches).

Then consult, in order of authority:

1. **The issue** being implemented. Find it by branch name (`feat/verb-table` → the feature directory whose slug
   matches), by the paths the diff touches, and by recent commit subjects. Read every issue file in that feature
   directory whole, not skimmed — the one being implemented, and its neighbours — because an issue often states what
   is deliberately left to a later one, and a later issue may record the reversal of an earlier one's decision. When
   code contradicts one issue, check the neighbours for the newer decision before calling the contradiction
   unrecorded: if a later issue records it, the finding is that the older issue was never updated, which is a
   different and smaller fix.
2. **The spec** for that feature — the Goal, Decisions, and any table or list the code must match.
3. **The ADRs the spec and the issue cite by number.**
4. **The standing rules** — `AGENTS.md` and/or `CLAUDE.md`: invariants, code style, where things go, and the
   workflow rules about tests and documentation.
5. **`CONTEXT.md`**: the glossary, including the `_Avoid_` synonyms.

Read them; do not recall them. These files change, and a review quoting a rule that no longer exists is worse than no
review. Where your instincts contradict what is written, the written source wins — and if the code is right and the
document is wrong, that is still a finding: the contradiction has to be reconciled, not ignored.

If you cannot tell which issue or spec governs the change — no feature directory matches, or several plausibly do —
stop and ask the author which one, listing the candidates you found. Reviewing against a guessed spec produces
confident findings about the wrong contract.

If the change is genuinely outside the tracked features (a chore, a dependency bump, a typo fix), or the repository
has no specs at all, degrade openly: review against the standing rules and glossary alone, and say so in the
verdict — "reviewed against standing rules only; no spec governs this change". Never present a degraded review as
full conformance. If the change is feature work with no spec behind it, add one line: a spec session would give this
change a contract worth reviewing against.

## Step 3 — Review through the lenses

Read [references/review-lenses.md](references/review-lenses.md) for the full catalog and use it as a checklist. The
lenses, in short:

1. **Spec conformance** — does the code do what the spec decided, including its tables and named values?
2. **Issue scope** — does it cover the issue's scope and test lists item by item, and has it done work the issue did
   not ask for?
3. **Declared invariants** — the safety and security rules the repository's documents state.
4. **Boundaries and layering** — the module and responsibility boundaries the documents draw.
5. **Code style rules** — the ones the standing rules state explicitly, which lint cannot check for you.
6. **Vocabulary** — names from `CONTEXT.md`, not the synonyms it tells you to avoid.
7. **Tests** — the failure paths, not only the happy path. A security-relevant fix needs a test that fails when the
   fix is removed.
8. **Documents now false** — anything the change has silently invalidated.
9. **Correctness** — the ordinary bugs: wrong boundary, unhandled null, swallowed exception, blocking call in async
   code.

## Step 4 — Verify each finding before you report it

For every candidate finding, produce three things: the file and line in the change, the exact sentence from the spec,
ADR, standing rules, or `CONTEXT.md` that it violates, and a concrete way it goes wrong. Drop anything you cannot pin
all three to — or, when the concern is real but the rule is not written, report it as a question, marked as such.

A finding without a citation is an opinion, and opinions in a conformance review are noise the author has to
personally re-verify.

An open question gets the same treatment in reverse: before reporting one, search the feature's spec and issues for
the answer. A question one of them already answers is not open — reporting it anyway is the review's own false
finding, and a false finding costs more trust than a missed one, because the author re-verifies everything else once
they catch it.

When a defect lives in a pattern — two messages sharing the same wrong remedy, a helper reused by both paths — name
every site that shares it. A fix applied to the first site found leaves the same bug standing next to it.

## Report format

Use this structure exactly, so the author can scan it the same way every time:

```markdown
# Conformance review: <feature slug or "uncommitted changes">

**Change set:** <N files, staged/unstaged/untracked — or the branch fallback, said plainly>
**Reviewed against:** <spec path, issue paths, ADR numbers, standing-rules files, CONTEXT.md — or "standing rules
only", said plainly>

## Verdict

<One or two sentences. Committed: ready to commit / needs changes before commit / cannot review, and why.>

## Findings

### 1. [blocker] <the defect in one line>

- **Where:** `path/to/file.py:120-134`
- **Rule:** "<quoted sentence>" — `<path of the document it comes from>`
- **Fails when:** <concrete input or state, and the wrong result>
- **Fix:** <the smallest change that satisfies the rule>

## Open questions

<Concerns with no written rule behind them, or things the documents leave ambiguous. Omit if none.>

## Checked and clean

<One line per lens you checked and found nothing. This is coverage, not praise — it tells the author what the
review actually covered.>

## Not covered

<What you could not judge and why: a file too large to read fully, behavior only a running test would settle, a
mandatory gate the author still has to run. Omit if none.>
```

Severities: **blocker** (violates the spec, an ADR, or a declared invariant; or is a bug), **major** (violates a
standing rule or leaves a document false), **minor** (small conformance slips — naming, a missing docstring, a test
that duplicates another). Order findings by severity, blockers first. If there are no findings at all, say so in the
verdict and still fill in "Checked and clean" — that section is what makes an empty review trustworthy.

Before delivering, re-read the report against itself. The verdict, the findings, and "Checked and clean" are one
document: a lens that produced a finding cannot also be declared clean, and an absolute claim — "every", "all",
"nothing" — is allowed only about a list you verified item by item. A report that contradicts itself makes the
author re-verify all of it, which is the cost this format exists to avoid.

## Example finding

### 1. \[blocker\] The refund path skips the idempotency key

- **Where:** `src/billing/refunds.py:88`
- **Rule:** "Every mutation carries an idempotency key; a call without one is refused." —
  `docs/features/refunds/spec.md`
- **Fails when:** a network retry re-posts the same refund without a key, and the provider processes it twice.
- **Fix:** Refuse the call when the key is absent; refusing is the direction the spec picks, and generating a
  fallback key is the fail-open direction it rules out.
