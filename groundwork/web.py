"""The one source for an app's public version string.

Every app in this estate served `version: 0.1.0` in its OpenAPI schema while its root page
showed the deployed tag — six copies of the same defect: `FastAPI()` was constructed
without a `version` argument, so FastAPI supplied its default while the front page read
`APP_VERSION` from the environment. Verified from outside on 2026-08-03.

The fix is one source, used by both consumers:

    from groundwork import build_version
    app = FastAPI(title="...", version=build_version())     # the schema
    html.replace("__VERSION__", build_version())            # the front page

`APP_VERSION` is baked by each app's Dockerfile from a build argument. An absent value
renders as "unreleased", never as a plausible-looking number.
"""
from __future__ import annotations

import os


def build_version() -> str:
    return os.getenv("APP_VERSION", "unreleased")
