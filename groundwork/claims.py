from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    skill_evidence = "skill_evidence"
    event_signal = "event_signal"
    commitment = "commitment"
    issue_aspect = "issue_aspect"
    doc_assertion = "doc_assertion"


class EvidenceRef(BaseModel):
    source: str
    span: Optional[tuple[int, int]] = None


class Extractor(BaseModel):
    model: str
    version: str
    temp: float = 0.0


class Verification(BaseModel):
    status: str = "pending"            # pending | passed | rejected
    gates: list[str] = Field(default_factory=list)
    score: Optional[float] = None


class Claim(BaseModel):
    """The atom of the whole portfolio. Bitemporal: observed_at is when the fact was
    true in the world, recorded_at is when the system learned it."""
    claim_id: str
    type: ClaimType
    statement: str
    evidence_ref: EvidenceRef
    observed_at: Optional[date] = None
    recorded_at: datetime
    extracted_by: Extractor
    confidence: Optional[float] = None
    verification: Verification = Field(default_factory=Verification)
