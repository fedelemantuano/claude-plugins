# Review lenses

The full catalog for Step 3 of the conformance review. Work through every lens; a lens with nothing to report earns
its line under "Checked and clean". Each finding a lens produces still has to pass Step 4 — file and line, quoted
rule, concrete failure.

## 1. Spec conformance

Compare the code against every decision the spec records: the Goal, the Decisions list, and any table, enum, or
named value the code must match. Tables are the highest-yield spot — check them cell by cell, because a code path
that handles nine rows of ten looks complete in a skim. A behaviour the spec decided against is a finding even when
the code's version is arguably better: the fix may be to change the spec, but the contradiction must surface, not
ship silently.

## 2. Issue scope

Take the issue's scope and test lists and tick them item by item against the diff. Two directions:

- **Under-delivery** — an item the issue lists that the change does not do. "Mostly done" is not done.
- **Over-delivery** — work the diff does that no issue asked for: an extra endpoint, a drive-by refactor, a new
  dependency. Unrequested work is unreviewed work; name it so the author can split it out or get it specced.

Check the neighbouring issues before calling something missing — it may be deliberately deferred to a later issue,
and that is not a finding.

## 3. Declared invariants

The safety and security rules the repository's documents state: fail closed, allowlist over blocklist, no secrets in
logs or errors, server-side enforcement, audit trails — whatever this repository wrote down. Only declared
invariants belong here; an invariant you believe in but cannot quote goes to "Open questions". Violations of a
declared invariant are blockers, and they hide in the error paths: check what happens on the miss, the timeout, and
the exception, not just the happy path.

## 4. Boundaries and layering

The module and responsibility boundaries the documents draw: which layer decides, which layer executes, what this
repository deliberately does not contain. A change that makes a lower layer take a decision the docs assign to an
upper one conforms to no spec, however clean the code. Import direction is the quick probe: a dependency arrow
pointing the way the docs forbid is usually the whole finding.

## 5. Code style rules

Only the rules the standing rules state explicitly — the ones lint cannot check: naming conventions, where new files
go, forbidden patterns, required docstrings, dependency policy ("every third-party import declared in the dependency
file"). If no written rule backs the observation, it is taste and does not belong in the report.

## 6. Vocabulary

Names in the diff — identifiers, log messages, doc headings — against the glossary in `CONTEXT.md`. Two failure
modes: using a synonym the glossary explicitly avoids, and coining a new term for a concept the glossary already
names. Vocabulary drift is usually minor, but flag it everywhere it appears: one wrong name copied into five files
is five renames later.

## 7. Tests

For each behaviour the change adds, ask which test fails if the behaviour is removed. Then check the failure paths
specifically: refused, invalid, timed out, expired, dependency down. A happy-path-only test suite for a change whose
spec is mostly about refusals has not tested the spec. A security-relevant fix without a test that fails when the
fix is reverted is a blocker, not a nice-to-have. Also check the tests themselves as code: a test that asserts
nothing, or duplicates a neighbour, is a finding.

## 8. Documents now false

Read every document that describes what the change touched: `README.md`, the spec, the ADRs, agent-facing docs. A
sentence the change has made untrue is a finding at the sentence level — quote it. This includes the pleasant
direction: code that improved past what an ADR records still leaves the ADR false.

## 9. Correctness

The ordinary bugs, confined to the changed lines: off-by-one and wrong comparison at boundaries, unhandled null or
empty input, swallowed or over-broad exception handlers, resources acquired but not released, blocking calls in
async code, races on shared state. Conformance does not excuse a crash — a change that matches the spec and still
breaks is "needs changes". These findings need no document citation; the concrete failure scenario carries them.
