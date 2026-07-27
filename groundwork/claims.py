from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Literal, Optional
from pydantic import AwareDatetime, BaseModel, Field


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
    status: Literal["pending", "passed", "rejected"] = "pending"
    gates: list[str] = Field(default_factory=list)
    score: Optional[float] = None


class Claim(BaseModel):
    """The atom of the whole portfolio. Bitemporal: observed_at is when the fact was
    true in the world (calendar-date resolution), recorded_at is the timezone-aware
    instant (UTC by convention) when the system learned it. recorded_at must be
    aware so cross-producer bitemporal ordering is never ambiguous."""
    claim_id: str
    type: ClaimType
    statement: str
    evidence_ref: EvidenceRef
    observed_at: Optional[date] = None
    recorded_at: AwareDatetime
    extracted_by: Extractor
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    verification: Verification = Field(default_factory=Verification)
