# webshell — the estate's shared frontend shell

Source of truth for the pieces every product demo shares: the design system CSS (charcoal +
deep green + gold, dark first with an honest light mode), the root layout, and `lib/`
(session hook against `POST /api/v1/demo/session`, the authed fetch wrapper mapping
401 to SESSION_EXPIRED and 429 to BUDGET_EXHAUSTED, and the honest error messages).

**Consumed by copy, deliberately.** A Docker build context cannot reach a sibling repo, so
each app vendors `web/shell/` from here with the provenance header intact. When this
directory changes, re-copy; the header names the source. Product-specific screens never
live here.

Extracted 2026-08-03 from CareerCompiler's shipped frontend (v0.3.1, production-verified).
