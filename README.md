# groundwork

> **Status: v0.1.0 (working library).** The code documented below is implemented and unit-tested:
> the Claim schema, the OpenRouter gateway, the config guard, verification gates, and tracing. The
> six portfolio apps depend on it; those apps are at scaffold stage (Phase 1 in progress).

Shared library for the AiGNITE portfolio. The LLM senses; deterministic code decides;
every claim carries provenance. `groundwork` is the spine every app imports so that
thesis is enforced the same way everywhere.

## What it ships

| Module | Responsibility |
|--------|----------------|
| `groundwork.claims` | `Claim`, the bitemporal, evidence-carrying atom of the whole portfolio, plus `ClaimType`, `EvidenceRef`, `Extractor`, `Verification`. |
| `groundwork.config` | `BaseConfig` (Pydantic settings) and `forbid_mock()`: Standard 3 enforced in code, no silent mock/fallback outside development. |
| `groundwork.gateway` | `LLMGateway`, the *only* sanctioned path to a model. OpenRouter (OpenAI-compatible), model IDs pinned from env, JSON-schema structured output, every call traced. |
| `groundwork.trace` | `record_call()`: every LLM call becomes a structured trace. This log stream is the raw material Seismograph will consume. |
| `groundwork.verification` | `Gate` protocol, `SchemaGate` (no naked claims), `NLIGate` (entailment interface; raises until an app injects a model). |

## Install

Standalone (as a dependency of your own project):

```bash
pip install "aignite-groundwork @ git+https://github.com/nuwansamaranayake/groundwork@v0.1.0"
```

For local development of groundwork itself:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (source .venv/bin/activate on POSIX)
pip install -e .[dev]
```

`uv` is preferred once available (`uv sync`); until then `pip` is the supported fallback.

## Use

```python
from groundwork import BaseConfig, LLMGateway, Claim, SchemaGate

cfg = BaseConfig()                    # reads .env / environment
gateway = LLMGateway(cfg)             # raises if OPENROUTER_API_KEY is unset; never runs blind
```

Apps subclass `BaseConfig` to add their own fields (database URL, model selections, connectors)
and depend on `aignite-groundwork`; during portfolio development they install it editable from the
sibling checkout (`pip install -e ../groundwork`).

## Verify

```bash
make test     # unit suite, this library's definition of "eval" (also: make eval)
make lint     # ruff
```

## Doctrine

Read `DOCTRINE.md`. Every rule there is enforced somewhere in this library. `NLIGate` raising
`NotImplementedError` until wired is deliberate: the portfolio would rather fail loud than fabricate.
