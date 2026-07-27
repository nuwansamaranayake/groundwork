# Changelog

All notable changes to groundwork are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-23

### Added
- CI pipeline (`.github/workflows/ci.yml`): ruff lint and unit tests on Python 3.12 and 3.13.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1) and a SECURITY.md vulnerability-reporting policy.
- `GatewayError`: typed error carrying model, finish_reason, and response id when a call yields
  no usable completion (empty choices or null content), replacing bare `IndexError`/`TypeError`.
- `configure_tracing()`: the `groundwork.trace` logger attaches a default stderr handler at import
  and honors `BaseConfig.log_level`, so traces emit without any app-side logging config.
- `BaseConfig` gains `llm_model_extraction` / `embedding_model` (the model-pinning vars
  `.env.example` ships now actually bind) and `llm_timeout_s` (default 30s) / `llm_max_retries`
  (default 2), passed to the OpenAI client so every gateway call is bounded; `complete()` accepts
  a per-call `timeout` override.
- `.dockerignore` so secrets (`.env`), git history, and caches can never enter a build context.
- `FAILURES.md` failure gallery, seeded with the adversarial review wave (FAIL-0001).

### Changed
- Tagged `v0.1.0` as the first consumable release; portfolio apps now depend on groundwork via a
  pinned git dependency (see `docs/adr/0003-groundwork-distribution.md`). PyPI publication planned.
- `Verification.status` is now `Literal["pending", "passed", "rejected"]` and `Claim.confidence`
  is constrained to [0.0, 1.0]; `Claim.recorded_at` must be timezone-aware (`AwareDatetime`).
- Trace `usage` is serialized as structured JSON (`model_dump()`), not a Python repr string.

### Fixed
- Failed LLM calls (timeout, 429, 5xx, auth) are now traced with `status="error"` before the
  exception re-raises; the trace stream no longer shows a success-only view during outages.
- The `[0.1.0]` entry below corrected to list what the tag actually shipped; the earlier entry
  claimed a smoke test, migration-count check, CI pipeline, and synthetic dataset that were not
  in the tagged tree.

## [0.1.0] - 2026-07-21
### Added
- Claim schema: `Claim` (bitemporal, evidence-carrying), `ClaimType`, `EvidenceRef`,
  `Extractor`, `Verification`.
- `LLMGateway`: the sole sanctioned LLM path (OpenRouter, OpenAI-compatible) with JSON-schema
  structured output.
- Config guard: `BaseConfig` and `forbid_mock()` — no silent mock/fallback outside development.
- Verification gates: `Gate` protocol, `SchemaGate`, `NLIGate` (raises until an app injects a model).
- `record_call()` trace logging.
- Governed doc set: DOCTRINE.md, CLAUDE.md, CONTRIBUTING.md, LICENSE (Apache-2.0).
