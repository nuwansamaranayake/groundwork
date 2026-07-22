# 3. groundwork distribution: pinned git dependency now, PyPI at release

Date: 2026-07-21

## Status

Accepted

## Context

Each app declared `aignite-groundwork` as an editable path dependency on `../groundwork`. That works
only when the two repos sit side by side. On GitHub every repo is a standalone checkout, so
`pip install -e .` fails for CI and for anyone who clones a single app: the first command a visitor
runs, fails. For a portfolio whose whole pitch is verified claims, that is the worst possible first
experience.

## Decision

Apps depend on groundwork via a **pinned git dependency**:

```
aignite-groundwork @ git+https://github.com/nuwansamaranayake/groundwork@v0.1.0
```

groundwork is tagged `v0.1.0`. The path/editable source entry (`[tool.uv.sources]`) is removed so a
standalone `pip install -e .[dev]` resolves groundwork entirely from GitHub.

Local portfolio development stays editable: install the sibling first
(`pip install -e ../groundwork`, then `pip install -e .[dev]`). pip treats an already-installed
distribution of the same name as satisfying the URL requirement, so the editable checkout wins locally.

PyPI publication of `aignite-groundwork` at `v0.1.0` is planned at first release; the git dependency
is replaced by a version specifier once published. A published package is itself a portfolio credential.

## Consequences

- Standalone clones and CI install with no sibling-checkout step.
- The dependency is reproducible and pinned to a tag, not a moving branch.
- Until groundwork is pushed and tagged, the URL does not resolve; this is expected and documented.
- One more release chore: cut a groundwork tag (and later a PyPI release) before the apps can pin to it.
