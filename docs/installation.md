# NEXUS-RE Installation Guide

> Version: 3.0.0 | Last Updated: 2026-10-16

This document describes how to install and run NEXUS-RE on Linux, macOS, Windows, and Android.

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Linux, macOS, Windows, Android | Linux (Ubuntu 22.04+) |
| RAM | 2 GB | 8 GB |
| Disk | 50 MB | 2 GB (for datasets) |
| Python | 3.11 | 3.13 |
| Node.js | Not required | Not required |

Core tools require no external dependencies. Everything runs on standard Python.

---

## Quick Install (All Platforms)

### Step 1: Install Python 3.11 or higher

Ubuntu / Debian:

sudo apt update
sudo apt install python3.13 python3-pip git -y

macOS (Homebrew):

brew install python@3.13 git

Windows: Download Python 3.13 from python.org and check "Add to PATH".

Android: Install Pydroid 3 (Play Store) or Termux (F-Droid).

### Step 2: Clone the repository

git clone https://github.com/qamarsobhy7-source/nexus-re.git
cd nexus-re

### Step 3: Verify installation

python -c "from nexus_re_v3 import calculate_hash; print(calculate_hash('NEXUS'))"

Expected output:

SHA256: 52b797a276d825aaa28f449f1d35682bd4d271f6455be84e3869cdd7aed2ca03
MD5:    d053b198d88b5d1bb38f86da8c17fdb6

That's it. No dependencies to install.

---

## Running the CLI

python nexus_re_v3.py

You will see:

=======================================================
  NEXUS-RE v3.0 - Reverse Engineering Toolkit
  21 Tools | File Analysis | Version Diff
=======================================================

--- BASIC (text input) ---
 1. Hex Dump
 2. Extract Strings
 3. Calculate Hash
 ...

Choose (0-21):

---

## Running the Multi-Agent System

python nexus_agents.py

Example:

Enter file path or hex string: 7f454c4602010100...

[Orchestrator] Session: 20261016_122358
[Orchestrator] Plan: static -> security -> crypto -> report

[Step 1/4] static: Static binary analysis
[Step 2/4] security: Threat detection
[Step 3/4] crypto: Cryptanalysis
[Step 4/4] report: Evidence synthesis

---

## Running the RAG Service

python nexus_rag.py

Example:

Ask a question: ransomware bitcoin

[MITRE-T1486] Data Encrypted for Impact (Ransomware)
  Severity: CRITICAL
  Score: 0.302

---

## Running the REST API

python api_render.py

Output:

[SERVER] NEXUS-RE API running on http://0.0.0.0:8000
[SERVER] Toolkit:  LOADED
[SERVER] Agents:   LOADED
[SERVER] RAG:      LOADED
[SERVER] Endpoints: 24

Test the API:

curl http://localhost:8000/health

---

## Running the Test Suite

python -m unittest tests.test_tools -v

Expected output:

Ran 27 tests in 0.016s

OK

---

## Optional: Install AI Agent Support

For MCP integration with Claude Code, Cursor, or Codex:

pip install mcp

Then register NEXUS-RE as an MCP server:

{
  "mcpServers": {
    "nexus-re": {
      "command": "python",
      "args": ["/path/to/nexus_re_server.py"]
    }
  }
}

Note: The MCP package requires Rust to be installed. On Termux:

pkg install rust
pip install mcp

---

## Optional: Install Docker

For containerized deployment:

docker build -t nexus-re:latest .
docker run -it --rm nexus-re:latest

Or with docker-compose:

docker compose up -d

---

## Android Installation (Pydroid 3)

Pydroid 3 is the easiest way to run NEXUS-RE on Android.

### Step 1: Install Pydroid 3

Download from Google Play Store or the official website.

### Step 2: Download nexus_re_v3.py

Save the file to /storage/emulated/0/Documents/.

### Step 3: Open in Pydroid 3

1. Open Pydroid 3
2. Tap Menu (three lines)
3. Select "Open"
4. Choose Documents
5. Tap nexus_re_v3.py

### Step 4: Run

Tap the yellow play button.

### Step 5: Save output

Long-press on any tool output to copy it.

---

## Android Installation (Termux)

Termux gives you a full Linux environment on Android.

### Step 1: Install Termux

Download from F-Droid (recommended) or GitHub releases.

### Step 2: Update and install Python

pkg update && pkg upgrade -y
pkg install python rust git -y

### Step 3: Install optional MCP

pip install mcp

### Step 4: Clone repository

git clone https://github.com/qamarsobhy7-source/nexus-re.git
cd nexus-re

### Step 5: Run

python nexus_re_v3.py

---

## Configuration File (Optional)

Create nexus-re.yaml in your home directory:

llm:
  provider: ollama
  model: llama3.1:8b
  temperature: 0.2

tools:
  ghidra_path: /opt/ghidra
  frida_enabled: false

ui:
  language: en
  theme: dark
  streaming: true

security:
  sandbox: true
  max_file_size_mb: 500
  timeout_seconds: 300

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| NEXUS_LLM_PROVIDER | LLM backend | ollama |
| NEXUS_LLM_MODEL | Model name | llama3.1:8b |
| NEXUS_GHIDRA_PATH | Ghidra install path | auto-detect |
| NEXUS_LOG_LEVEL | Logging level | INFO |
| NEXUS_SANDBOX | Sandbox dynamic runs | true |

---

## Troubleshooting

### ImportError: No module named mcp

Run:

pip install mcp

Only needed for AI-agent integration.

### FileNotFoundError: ghidra

Set NEXUS_GHIDRA_PATH or install Ghidra from ghidra-sre.org.

### Slow analysis on large files (over 100 MB)

Increase timeout_seconds in config, or use full_analysis on a trimmed hex substring.

### UnicodeDecodeError on Windows

Set environment variable:

set PYTHONIOENCODING=utf-8

### Pydroid 3 crashes when opening large files

Close other apps to free memory. Pydroid 3 needs at least 500 MB RAM to open the full nexus_re_v3.py file.

---

## Verifying the Installation

Run this checklist:

python -c "from nexus_re_v3 import calculate_hash; print(calculate_hash('NEXUS'))"
python -c "from nexus_agents import Orchestrator; print('Agents OK')"
python -c "from nexus_rag import RAGService; print('RAG OK')"
python -m unittest tests.test_tools

All 4 commands should succeed.

---

## Next Steps

After installation:

1. Read docs/architecture.md to understand the system
2. Read docs/cli.md for the CLI reference
3. Read docs/testing.md to run the test suite
4. Read docs/evidence.md to understand the evidence system
5. Read docs/roadmap.md for planned features

---

## Getting Help

- Documentation: See the docs/ folder
- Bug Reports: https://github.com/qamarsobhy7-source/nexus-re/issues
- Discussions: https://github.com/qamarsobhy7-source/nexus-re/discussions

---

## References

- Python 3.13: https://www.python.org
- Pydroid 3: https://play.google.com/store/apps/details?id=ru.iiec.pydroid3
- Termux: https://f-droid.org/en/packages/com.termux/
- Docker: https://docs.docker.com/get-docker/
- Model Context Protocol: https://modelcontextprotocol.io