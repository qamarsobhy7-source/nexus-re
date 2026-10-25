# NEXUS-RE for AI Agents

This document helps AI coding agents (Cursor, Copilot, Claude Code, Windsurf, etc.) understand how to work with the NEXUS-RE repository.

## Project Overview
NEXUS-RE is an AI-ready reverse engineering platform. It exposes 31 pure-Python analysis tools via an MCP server, a REST API, and a static web dashboard.

## Key Commands
- **Run CLI:** `python nexus_re_v3.py`
- **Run Tests:** `python -m unittest tests.test_tools -v`
- **Health Check:** `python doctor.py`
- **Run API:** `python api_render.py`
- **Build Docker:** `docker build -t nexus-re:latest .`

## Code Structure
- `src/tools/nexus_re_v3.py`: The 31 analysis tools.
- `src/agents/nexus_agents.py`: The 4 specialist agents.
- `src/rag/nexus_rag.py`: TF-IDF retrieval engine.
- `src/api/api.py`: Pure-Python HTTP server.
- `tests/test_tools.py`: 27 unit tests.

## Guidelines for AI Agents
1. All tools must be deterministic (same input -> same output).
2. Every tool must return a formatted string report.
3. New tools must be added to the `hex_tools` or `text_tools` dictionary in `nexus_re_v3.py`.
4. Always run `python doctor.py` before committing.
