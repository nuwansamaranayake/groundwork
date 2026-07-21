from typing import Protocol
from .claims import Claim


class Gate(Protocol):
    """A deterministic verification gate. Perception proposes, verification disposes."""
    name: str
    def check(self, claim: Claim) -> bool: ...


class SchemaGate:
    """Passes if the claim is well-formed and carries evidence. No naked claims."""
    name = "schema"
    def check(self, claim: Claim) -> bool:
        return bool(claim.evidence_ref.source and claim.statement)


class NLIGate:
    """Interface for the entailment gate. Apps inject a cross-encoder NLI model.
    Raises until wired, per the no-fabrication rule."""
    name = "nli_entailment"
    def check(self, claim: Claim) -> bool:
        raise NotImplementedError("Inject an NLI model at the app layer before using NLIGate.")
