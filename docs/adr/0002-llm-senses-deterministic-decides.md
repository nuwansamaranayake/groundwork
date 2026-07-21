# 2. The LLM senses; deterministic code decides

Date: 2026-07-21

## Status

Accepted

## Context

Most LLM applications let the model both perceive *and* decide: it reads messy input and then
directly emits the answer, the score, the ranking, the action. That couples an unreliable,
non-deterministic component to consequential output. When it drifts, there is no seam at which
to catch the error, and it fails silently — the exact failure mode that cost GoviHub five days
(see `DOCTRINE.md`).

## Decision

Across the entire AiGNITE portfolio the LLM is a **sensor, not a judge**:

1. The LLM turns unstructured reality into typed, provenance-carrying **`Claim`** objects.
2. Deterministic code **verifies** those claims through explicit `Gate`s, **decides**, and
   **computes every number**.
3. Humans approve anything that acts.

`groundwork` encodes this: `Claim` (perception with evidence), `Gate`/`SchemaGate`/`NLIGate`
(deterministic disposition), `LLMGateway` (the single traced perception channel). `NLIGate`
raises until an app injects a real model rather than silently passing.

## Consequences

- There is always a seam — the claim boundary — at which to measure, test, and reject.
- Non-determinism is quarantined to perception; decisions are reproducible and unit-testable.
- The same skeleton (`Claim` in, gated decision out) generalizes across all six apps, which is
  what makes the portfolio a coherent argument rather than six unrelated demos.
- Cost: an extra modeling step (claims + gates) that a naive "prompt returns the answer" app skips.
  That cost is the point.
