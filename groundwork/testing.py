"""Shared test assertions and fakes for the estate's apps.

Import these in an app's suite rather than copying them: a per-app copy drifts, and the
estate has already paid for that lesson twice (the `{id}` vs `{cid}` contracts drift, and
six identical missing-version defects).
"""
from __future__ import annotations

import re

_VERSION_RE = re.compile(r"version <code>([^<]+)</code>")


def assert_served_version_matches_front_page(client) -> None:
    """The served OpenAPI version and the root page must come from the same source.

    `client` is a fastapi.testclient.TestClient (or anything with .get returning
    .text/.json). The front pages across this estate render the build stamp as
    `version <code>X</code>`; if an app changes that markup, this assertion fails loudly
    rather than silently checking nothing.
    """
    html = client.get("/").text
    m = _VERSION_RE.search(html)
    assert m, ("the front page no longer renders 'version <code>...</code>'; "
               "update groundwork.testing to match the new markup, do not delete the check")
    rendered = m.group(1)
    served = client.get("/openapi.json").json()["info"]["version"]
    assert served == rendered, (
        f"openapi.json says {served!r} but the front page says {rendered!r}; both must "
        "come from groundwork.build_version()")


class FakeRedis:
    """The slice of redis the demo kit uses, with a manual expiry lever for tests."""

    def __init__(self):
        self.store: dict[str, dict] = {}
        self.counters: dict[str, int] = {}

    def hset(self, key, mapping):
        self.store.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})

    def hget(self, key, field):
        return self.store.get(key, {}).get(field)

    def hincrby(self, key, field, n):
        v = int(self.store.setdefault(key, {}).get(field, 0)) + n
        self.store[key][field] = str(v)
        return v

    def exists(self, key):
        return 1 if key in self.store else 0

    def incr(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key, ttl):
        return True

    def expire_now(self, key):
        """What Redis does at TTL, done on demand."""
        self.store.pop(key, None)
