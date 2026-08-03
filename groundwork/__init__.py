"""aignite-groundwork: the shared spine of the AiGNITE portfolio.

The LLM senses. Deterministic code decides. Every claim carries provenance.
"""
from .claims import Claim, ClaimType, EvidenceRef, Extractor, Verification
from .config import BaseConfig, Env, forbid_mock
from .gateway import GatewayError, LLMGateway
from .trace import configure_tracing, record_call
from .verification import Gate, SchemaGate, NLIGate
from .web import build_version
from .demokit import DemoKit, DemoRefused, ScopeDenied, guard_prefix, new_tenant_prefix

__version__ = "0.2.0"

__all__ = [
    "build_version",
    "DemoKit",
    "DemoRefused",
    "ScopeDenied",
    "guard_prefix",
    "new_tenant_prefix",
    "Claim",
    "ClaimType",
    "EvidenceRef",
    "Extractor",
    "Verification",
    "BaseConfig",
    "Env",
    "forbid_mock",
    "GatewayError",
    "LLMGateway",
    "configure_tracing",
    "record_call",
    "Gate",
    "SchemaGate",
    "NLIGate",
]
