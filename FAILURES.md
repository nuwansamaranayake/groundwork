# Failure Gallery — groundwork

An honest record of things that broke, why, and what changed. A curated gallery beats a buried
changelog: it is where the doctrine earns its keep. Every entry names the *reported* symptom and
the *diagnosed* root cause separately (Standard 5).

## FAIL-0001 — Adversarial review wave: 10 confirmed findings, zero refuted, before release

- **Date**: 2026-07-27
- **Surface**: the whole library — `trace.py`, `gateway.py`, `claims.py`, `config.py`, and the
  governed docs (CHANGELOG, README, SECURITY.md, CLAUDE.md).
- **Reported symptom**: none. The unit suite was green and everything "worked". An adversarial
  code review of the v0.1.x tree confirmed 10 findings (2 major, 8 minor); none were refuted.
- **Diagnosed causes** (worst first):
  - **Every trace was silently discarded by default** (major): `record_call` logged at INFO on a
    handler-less logger, and nothing in groundwork or any app attached a handler, so under
    Python's last-resort handler (WARNING+) the "raw material for Seismograph" never emitted.
    Reproduced: fresh interpreter, `record_call(...)` printed nothing.
  - **CHANGELOG claimed artifacts that never existed** (major): the `[0.1.0]` entry listed a smoke
    test, migration-count check, CI pipeline, and synthetic dataset; `git ls-tree v0.1.0` contains
    none of them.
  - Failed LLM calls skipped `record_call` entirely, giving Seismograph a success-only view during
    outages; empty choices / null content raised bare `IndexError`/`TypeError` instead of a typed
    error; `usage` was serialized as a Python repr string, not structured JSON; the sole
    sanctioned LLM path had no timeout bound (SDK defaults: ~30 min worst case);
    `Verification(status="passd")` and `confidence=7.5` validated silently; `recorded_at` accepted
    naive datetimes, so bitemporal ordering raises the moment any producer uses aware timestamps;
    README/CLAUDE/SECURITY overclaimed enforcement ("every rule enforced", "pins model IDs from
    env", embedding pinning with zero embedding code).
- **Root cause**: the library shipped against its own doctrine on self-assessment alone. The docs
  asserted properties the code did not implement, and no adversarial pass had ever run.
- **Fix**: all 10 findings fixed in one wave — default trace handler + `configure_tracing()`,
  error-path tracing, typed `GatewayError`, structured `usage`, timeout/retry bounds bound from
  config, `Literal` status + bounded confidence + `AwareDatetime`, and every doc claim rewritten
  to match observed reality. Regression tests added for each behavior change (16 tests green).
- **Doctrine link**: Standard 1 (fix root causes), Standard 3 (fail loud with typed errors),
  Standard 5 (document actually-broken vs reported). The adversarial review caught all of this
  before any release consumed it.
