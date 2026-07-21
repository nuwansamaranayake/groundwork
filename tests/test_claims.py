from datetime import date, datetime

import pytest

from groundwork import (
    BaseConfig,
    Claim,
    ClaimType,
    Env,
    EvidenceRef,
    Extractor,
    SchemaGate,
    forbid_mock,
)


def _claim() -> Claim:
    return Claim(
        claim_id="c1",
        type=ClaimType.skill_evidence,
        statement="Led migration of ten services to async I/O.",
        evidence_ref=EvidenceRef(source="resume.pdf", span=(120, 180)),
        observed_at=date(2025, 3, 1),
        recorded_at=datetime(2026, 7, 21, 8, 0, 0),
        extracted_by=Extractor(model="test-extractor", version="0.0.1"),
        confidence=0.9,
    )


def test_schema_gate_passes_on_well_formed_claim():
    assert SchemaGate().check(_claim()) is True


def test_schema_gate_rejects_claim_without_evidence():
    c = _claim()
    c.evidence_ref.source = ""
    assert SchemaGate().check(c) is False


def test_forbid_mock_raises_outside_development():
    cfg = BaseConfig(app_env=Env.production)
    with pytest.raises(RuntimeError):
        forbid_mock(cfg, "demo fixture")


def test_forbid_mock_allows_development():
    cfg = BaseConfig(app_env=Env.development)
    forbid_mock(cfg, "demo fixture")  # must not raise
