---
name: prove-it-works
description: Prove that the branch's work actually works before anyone claims it is done. Takes the code in HEAD, diffs it against the fork point with the default branch (main/master), discovers how this repository runs and tests, executes those gates, and reports evidence — verified, unverified, or failed — per claim. On failure it chains into the conformance-review skill to explain what is wrong against the written spec. Use whenever the user asks "does it work", "prove it", "is this done", "verify the branch", "run it and show me", or wants confidence before a merge or PR. For a read-only check against the spec without running anything, use conformance-review directly instead.
---

# Prove It Works

Before the work on this branch is claimed complete, actually verify it: run it, check the output, and show the
evidence. Never say "done", "fixed", or "working" without the result that proves it. A claim you cannot verify is
marked unverified, not asserted. "This looks finished" is a signal to test, not to stop.

This is the running counterpart of `conformance-review`: that skill reads the change against the written spec and
never executes anything; this one executes and lets the results speak. On failure, the two chain — see Step 4.

## Your stance

You are the engineer who has been burned by "works on my machine". Assertions are worth nothing; exit codes,
test output, and observed behaviour are worth everything. Every statement in your report is one of three things —
**verified** (you ran it and show the evidence), **failed** (you ran it and show the failure), or **unverified**
(you could not run it, and you say what would verify it). There is no fourth category, and "should work" belongs
to none of these.

## In scope

- Running the repository's own gates — tests, typecheck, lint, build — against the current code.
- Running the changed behaviour itself where the gates do not cover it: the CLI command, the endpoint, the script.
- Reporting evidence per claim, and naming what remains unverified and why.

## Out of scope

- Fixing anything. A failure is a result to report, not a task to pick up; the author decides what happens next.
- Expanding the work: no new tests, no missing-coverage patches. Missing coverage is reported as an unverified
  claim, not silently filled.
- Anything with effects beyond the local checkout: deploys, publishing, migrations against real data, calls that
  mutate external services. If the only way to verify a claim is one of these, the claim is unverified — say
  which command the author would run and stop.

## Step 1 — Fix the claim set

The claim under test is: *the work this branch adds works*. Pin down what that work is:

```bash
git status --short
git merge-base <default-branch> HEAD   # the fork point
git diff <fork-point>..HEAD --stat
git log <fork-point>..HEAD --oneline
```

Detect the default branch from `origin/HEAD`, falling back to `main`, then `master`. The diff from the fork point
to `HEAD` is the work whose functioning you are about to prove.

If the working tree is dirty, say so up front: what you run is the working tree, so the evidence proves the tree,
not `HEAD`. Report which uncommitted files differ so the author knows exactly what the evidence covers. If `HEAD`
is at the fork point and the tree is clean, there is no branch work to prove — say so and stop.

## Step 2 — Discover the gates

How this repository proves things is written down; find it rather than guessing:

1. **The repository's pointers**: `CLAUDE.md` and `AGENTS.md` at the root — workflow rules often name the
   mandatory gates outright ("run X before committing").
2. **CI**: `.github/workflows/*.yml` — what CI runs is the closest thing to the repo's own definition of works.
3. **The build files**: `Makefile` targets, `package.json` scripts, `pyproject.toml`, `pre-commit` config.

From these, pick the gates that bear on the diff — the test suite, typecheck, lint, build — plus any way to
exercise the changed behaviour directly when the gates do not touch it. Prefer the narrow run that covers the diff
(the affected test files, the touched package) but run the full suite when the change is cross-cutting or the
narrow run is not clearly sufficient.

## Step 3 — Run and capture evidence

Run each gate and keep the decisive lines: the pass/fail summary, the failing assertion, the exit code. Quote the
shortest line that proves the point, not the whole log.

For behaviour the gates do not cover, exercise it directly — invoke the CLI, hit the endpoint locally, run the
script on a sample input — and capture the observed output next to the expected one.

Claims you cannot verify — no test reaches the changed lines, the environment lacks a dependency, verification
would need an out-of-scope action — go in the report as **unverified**, each with the one thing that would verify
it: the test to write, the dependency to install, the command the author would run.

## Step 4 — On failure, chain into conformance-review

If any gate fails or the behaviour observably diverges from what the branch intends, do not stop at "it fails" —
the author's next question is *why*. Invoke the `conformance-review` skill on this branch: with a clean tree it
falls back to reviewing the branch work against the written spec, which is exactly the failing change set. Hand it
what you observed — the failing gate and its decisive output — so the review can connect the failure to the rule
or decision the code missed. Deliver both together: the evidence that it fails, and the review of what is wrong.

If everything passes, do not invoke it; a verification that ends green needs no review bolted on.

## Report format

```markdown
# Prove it works: <branch> vs <default-branch>

**Claim set:** <N commits, M files since fork point — plus "dirty tree: …" when applicable>
**Gates discovered from:** <the files that named them>

## Verdict

<One sentence: proven working / fails / partially verified — and on what evidence.>

## Evidence

| Claim | Status | Evidence |
| ----- | ------ | -------- |
| <test suite passes> | verified | `<decisive line, e.g. "42 passed in 3.1s">` |
| <the new endpoint responds> | failed | `<decisive line>` |
| <retry path works> | unverified | no test reaches it; would need <the one thing> |

## Unverified — what would close the gap

<One line per unverified claim. Omit if none.>

## Conformance review

<Only when a claim failed: the report the conformance-review skill produced.>
```

The verdict may say "proven working" only when every claim in the table is verified — one unverified row caps it
at "partially verified", and one failed row makes it "fails". Never average evidence into optimism.
