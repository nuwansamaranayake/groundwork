"""aignite-groundwork: the shared spine of the AiGNITE portfolio.

The LLM senses. Deterministic code decides. Every claim carries provenance.
"""
from .claims import Claim, ClaimType, EvidenceRef, Extractor, Verification
from .config import BaseConfig, Env, forbid_mock
from .gateway import LLMGateway
from .verification import Gate, SchemaGate, NLIGate

__version__ = "0.1.0"

__all__ = [
    "Claim",
    "ClaimType",
    "EvidenceRef",
    "Extractor",
    "Verification",
    "BaseConfig",
    "Env",
    "forbid_mock",
    "LLMGateway",
    "Gate",
    "SchemaGate",
    "NLIGate",
]
