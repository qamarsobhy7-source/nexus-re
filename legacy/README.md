# Legacy Code

This directory contains **old versions** of NEXUS-RE, kept for historical
reference only. They are **not part of the active codebase**.

## Files

| File | Version | Status | Notes |
|------|---------|--------|-------|
| `nexus_re_v1.py` | v1 (Phase 1) | 🚫 Deprecated | Initial prototype, 12 tools |
| `nexus_re_v2.py` | v2 (Phase 2) | 🚫 Deprecated | Expanded to 19 tools |

## Current version

See [`nexus_re_v3.py`](../nexus_re_v3.py) in the repo root — **33 tools,
4 agents, RAG, REST API** (56 passing tests).

## Why keep these?

- Historical record of the project's evolution
- Reference for how the architecture improved over time
- Educational: shows the incremental development path

**Do not use these files in new code.** They are not imported by any active
module and are not tested in CI.
