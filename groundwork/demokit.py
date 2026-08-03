"""Credential-less demo access, extracted from CareerCompiler so products three through
six cost a fraction of product two.

The shape, proven in production on 2026-08-03: a stranger gets a scoped, short-lived,
budgeted bearer token bound to a tenant prefix `demo-YYYYMMDDTHHMMSSZ-<6hex>-`. Every row a
session creates carries the prefix, which buys three properties at once: scope checks are a
string comparison against the row an id resolves to, the estate retention sweep in
portfolio-ops reclaims demo rows by the same prefix-match rule the monitor uses (retention
deliberately stays THERE — this module must never grow a second implementation), and a
seeded row is always distinguishable from a real one.

The estate invariant is untouched: the kit changes who can hold a bearer, never whether one
is required. No token stays 401 everywhere.

groundwork takes no redis or fastapi dependency for this: the redis client is duck-typed
(hset/hget/hincrby/exists/incr/expire — `groundwork.testing.FakeRedis` implements it), and
refusals raise `DemoRefused`, which the app's auth helper maps to its HTTP layer.
"""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timezone

TENANT_RE = re.compile(r"^demo-\d{8}T\d{6}Z-[0-9a-f]{6}-")


class DemoRefused(Exception):
    """A demo-session refusal with the HTTP semantics the app should surface."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ScopeDenied(DemoRefused):
    def __init__(self):
        super().__init__(403, "this demo session cannot access that resource")


def new_tenant_prefix(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return f"demo-{now.strftime('%Y%m%dT%H%M%S')}Z-{secrets.token_hex(3)}-"


def guard_prefix(scope: str | None, *values: str | None) -> None:
    """Tenancy as a string comparison. `scope is None` means full (estate-token) access;
    otherwise every value must carry the session's prefix. A missing row denies rather
    than reveals."""
    if scope is None:
        return
    for v in values:
        if v is None or not v.startswith(scope):
            raise ScopeDenied()


class DemoKit:
    """Sessions in redis: TTL is the expiry, a counter is the budget, an IP-keyed counter
    rate-limits creation. Nothing to migrate; an expired session disappears."""

    def __init__(self, redis, *, ttl_seconds: int = 1800, request_budget: int = 60,
                 sessions_per_ip_hour: int = 10):
        self.r = redis
        self.ttl = ttl_seconds
        self.budget = request_budget
        self.ip_limit = sessions_per_ip_hour

    def create_session(self, client_ip: str) -> tuple[str, str]:
        ip_key = f"demo:ip:{client_ip}"
        n = self.r.incr(ip_key)
        if n == 1:
            self.r.expire(ip_key, 3600)
        if n > self.ip_limit:
            raise DemoRefused(
                429, "demo session rate limit reached for this address; try again later")
        token = secrets.token_urlsafe(24)
        prefix = new_tenant_prefix()
        key = f"demo:{token}"
        self.r.hset(key, mapping={"prefix": prefix, "used": 0})
        self.r.expire(key, self.ttl)
        return token, prefix

    def check_session(self, token: str) -> str | None:
        """The tenant prefix for a live token, None when it is not a demo session (the
        caller then falls through to its 401). Expiry needs no code path: redis drops the
        key. The budget is a counter, not a clock."""
        key = f"demo:{token}"
        if not self.r.exists(key):
            return None
        used = self.r.hincrby(key, "used", 1)
        if used > self.budget:
            raise DemoRefused(429, "demo request budget exhausted; open a new session")
        return self.r.hget(key, "prefix")
