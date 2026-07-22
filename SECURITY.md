# Security — groundwork

`groundwork` is not a network service, but it is the single chokepoint for every model call
in the portfolio, so its security posture is inherited by all six apps. Baseline: **OWASP Top 10
for LLM Applications (2025)** and the **NIST AI Risk Management Framework — Generative AI Profile
(NIST AI 600-1)**.

## OWASP LLM Top 10 — where groundwork helps

| ID | Risk | groundwork control |
|----|------|--------------------|
| LLM01 | Prompt Injection | The gateway forces JSON-schema structured output, shrinking the blast radius of injected instructions; apps still validate every extracted `Claim` through a `Gate` before it can act. |
| LLM02 | Sensitive Information Disclosure | `trace.record_call()` logs a **prompt hash**, model, latency, and usage — never raw prompt or completion text. Secrets stay in env, never in logs. |
| LLM04 | Data & Model Poisoning | Claims carry `evidence_ref` + `extracted_by` provenance; `SchemaGate` rejects naked claims with no source. |
| LLM05 | Improper Output Handling | Structured output + downstream deterministic gates mean model text is treated as an untrusted proposal, never as a decision. |
| LLM06 | Excessive Agency | The library computes nothing consequential; it only *proposes* claims. Decisions and actions live in app-layer deterministic code with human approval. |
| LLM08 | Vector/Embedding Weaknesses | Embedding model IDs are pinned from env, not hardcoded, so a poisoned/deprecated model can be swapped centrally. |
| LLM09 | Misinformation | The whole design — sense vs. decide, provenance on every claim — exists to keep unverified model output from masquerading as fact. |

## NIST GenAI baseline

- **Govern**: one gateway, one trace format, one config guard — centralized, auditable.
- **Map**: `Claim` provenance (`observed_at`, `recorded_at`, `extracted_by`) makes lineage explicit.
- **Measure**: traces feed Seismograph's statistical process control.
- **Manage**: `forbid_mock()` makes silent degradation impossible outside development.

## Secrets

`OPENROUTER_API_KEY` is read from the environment only. `.env` is gitignored. `LLMGateway`
refuses to construct without a key rather than falling back to an unauthenticated call.

## Reporting a vulnerability

Report suspected vulnerabilities privately to **nuwans@hotmail.com**. Do not open a public issue.
You will receive an acknowledgment within 72 hours. Please allow time to investigate and ship a fix
before any public disclosure; a coordinated disclosure timeline will be agreed with you.
