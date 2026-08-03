"""B3: the demo kit's three properties, proven once here rather than per app.

Cross-tenant isolation, request budget, expiry — plus the prefix shape retention depends
on, and the rate limit on session creation.
"""
import pytest

from groundwork.demokit import DemoKit, DemoRefused, ScopeDenied, TENANT_RE, guard_prefix
from groundwork.testing import FakeRedis


@pytest.fixture()
def kit():
    return DemoKit(FakeRedis(), ttl_seconds=60, request_budget=3, sessions_per_ip_hour=2)


def test_session_prefix_has_the_retention_shape(kit):
    """The estate sweep reclaims demo rows by prefix match on demo-<stamp>Z-<hex>-;
    a prefix that drifts from this shape is a row retention can never reclaim."""
    _, prefix = kit.create_session("1.2.3.4")
    assert TENANT_RE.match(prefix), prefix


def test_a_demo_token_cannot_read_another_tenants_rows(kit):
    ta, pa = kit.create_session("1.1.1.1")
    tb, pb = kit.create_session("2.2.2.2")
    assert pa != pb
    guard_prefix(kit.check_session(ta), f"{pa}My Document")           # own row: fine
    with pytest.raises(ScopeDenied):
        guard_prefix(kit.check_session(ta), f"{pb}Their Document")    # cross-tenant: 403
    with pytest.raises(ScopeDenied):
        guard_prefix(kit.check_session(tb), f"{pa}My Document")
    guard_prefix(None, f"{pa}My Document")                            # estate token: full


def test_a_missing_row_denies_rather_than_reveals(kit):
    t, _ = kit.create_session("1.1.1.1")
    with pytest.raises(ScopeDenied):
        guard_prefix(kit.check_session(t), None)


def test_the_request_budget_is_a_counter_that_refuses_loudly(kit):
    t, _ = kit.create_session("1.1.1.1")
    for _ in range(3):
        assert kit.check_session(t)
    with pytest.raises(DemoRefused) as e:
        kit.check_session(t)
    assert e.value.status_code == 429


def test_an_expired_token_is_any_other_bad_bearer(kit):
    t, _ = kit.create_session("1.1.1.1")
    assert kit.check_session(t)
    kit.r.expire_now(f"demo:{t}")
    assert kit.check_session(t) is None, "expired must fall through to the app's 401"


def test_session_creation_is_rate_limited_per_address(kit):
    kit.create_session("9.9.9.9")
    kit.create_session("9.9.9.9")
    with pytest.raises(DemoRefused) as e:
        kit.create_session("9.9.9.9")
    assert e.value.status_code == 429
    kit.create_session("8.8.8.8")   # a different address is unaffected
