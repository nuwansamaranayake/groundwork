from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from groundwork import (
    BaseConfig,
    Claim,
    ClaimType,
    Env,
    EvidenceRef,
    Extractor,
    SchemaGate,
    Verification,
    forbid_mock,
)


def _claim(**overrides) -> Claim:
    kwargs = dict(
        claim_id="c1",
        type=ClaimType.skill_evidence,
        statement="Led migration of ten services to async I/O.",
        evidence_ref=EvidenceRef(source="resume.pdf", span=(120, 180)),
        observed_at=date(2025, 3, 1),
        recorded_at=datetime(2026, 7, 21, 8, 0, 0, tzinfo=timezone.utc),
        extracted_by=Extractor(model="test-extractor", version="0.0.1"),
        confidence=0.9,
    )
    kwargs.update(overrides)
    return Claim(**kwargs)


def test_schema_gate_passes_on_well_formed_claim():
    assert SchemaGate().check(_claim()) is True


def test_schema_gate_rejects_claim_without_evidence():
    c = _claim()
    c.evidence_ref.source = ""
    assert SchemaGate().check(c) is False


def test_verification_rejects_unknown_status():
    with pytest.raises(ValidationError):
        Verification(status="passd")


def test_confidence_must_be_within_unit_interval():
    with pytest.raises(ValidationError):
        _claim(confidence=7.5)
    with pytest.raises(ValidationError):
        _claim(confidence=-0.1)


def test_recorded_at_must_be_timezone_aware():
    with pytest.raises(ValidationError):
        _claim(recorded_at=datetime(2026, 7, 21, 8, 0, 0))


def test_forbid_mock_raises_outside_development():
    cfg = BaseConfig(app_env=Env.production)
    with pytest.raises(RuntimeError):
        forbid_mock(cfg, "demo fixture")


def test_forbid_mock_allows_development():
    cfg = BaseConfig(app_env=Env.development)
    forbid_mock(cfg, "demo fixture")  # must not raise
