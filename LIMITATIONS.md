# NEXUS-RE Limitations

> **Honest documentation of what this project CANNOT do.**
> This file exists because being transparent about limitations builds more trust than hiding them.

---

## 🚫 What NEXUS-RE Cannot Do (Yet)

### 1. No Real AI/LLM Integration

- **Current state:** The RAG service uses **TF-IDF** (a classic keyword-matching technique).
- **What is missing:** Real LLM integration (Llama 3, Mistral, Jais) with neural embeddings.
- **Impact:** Semantic understanding is limited. The system matches keywords, not meaning.
- **Roadmap:** Tracked in [Issue #20](https://github.com/qamarsobhy7-source/nexus-re/issues/20).

### 2. No Professional RE Tool Integration

- **Current state:** Parses ELF/PE headers only. No actual decompilation.
- **What is missing:** Ghidra, Frida, IDA Pro, radare2, JADX integration.
- **Impact:** Cannot decompile binaries to pseudocode, cannot trace runtime behavior.
- **Roadmap:** [Issue #18](https://github.com/qamarsobhy7-source/nexus-re/issues/18) (Ghidra), [Issue #19](https://github.com/qamarsobhy7-source/nexus-re/issues/19) (Frida).

### 3. No Dynamic Analysis

- **Current state:** 100% static analysis.
- **What is missing:** Sandboxed execution, system call tracing, network monitoring.
- **Impact:** Cannot observe what a binary actually DOES when executed.

### 4. Limited File Format Support

- **Fully supported:** ELF (Linux), PE (Windows), Mach-O (magic-number only).
- **Not supported:** .NET assemblies, Android APK, Firmware/IoT, EVM bytecode, WASM.
- **Planned:** See [Issues #18-#23](https://github.com/qamarsobhy7-source/nexus-re/issues).

### 5. No Real Benchmarking

- **Current state:** 56 unit tests + 10-sample mini-benchmark (all synthetic).
- **What is missing:** Evaluation on Decompile-Bench (2M samples), R3-Bench (~8K), BinMetric (~10K).
- **Impact:** No comparison with LLM4Decompile, GPT-4o, or human analysts.
- **Roadmap:** [Issue #22](https://github.com/qamarsobhy7-source/nexus-re/issues/22).

### 6. Simple Web Dashboard

- **Current state:** Single-file `index.html` with real browser-based analysis (8 JS tools). Full analysis is available via the Python CLI/API.
- **What is missing:** Next.js + React Flow + Monaco Editor for full interactive experience.
- **Roadmap:** [Issue #21](https://github.com/qamarsobhy7-source/nexus-re/issues/21).

### 7. MCP Server Has 16 Tools (Not 31)

- **Current state:** The MCP server (`nexus_re_server.py`) exposes only 16 tools.
- **What is missing:** The 15 advanced tools from `nexus_re_v3.py`.
- **Roadmap:** [Issue #23](https://github.com/qamarsobhy7-source/nexus-re/issues/23).

---

## ⚠️ Performance & Scale Limits

| Metric | Current | Why |
|--------|---------|-----|
| Max file size | ~50 MB | Memory limits on Android |
| Avg analysis time | 0.8s (small files) | No optimization yet |
| Concurrent users | 1-2 | Pure-Python HTTP server, no workers |
| Throughput | ~10 requests/min | No caching, no CDN |
| RAG latency | <10ms | TF-IDF is fast but shallow |

---

## 🔒 Security Boundaries

### What This Project IS
- ✅ A learning tool for reverse engineering concepts
- ✅ A reference architecture for AI-agent orchestration
- ✅ A demonstration that complex systems can be built on mobile

### What This Project IS NOT
- ❌ A replacement for Ghidra or IDA Pro
- ❌ A production-grade malware analysis platform
- ❌ A certified security tool

### Handling Real Malware
**DO NOT** run this on real malware without:
- An isolated sandbox (VM, container)
- No network access
- Snapshot capability
- Legal authorization

See [SECURITY.md](SECURITY.md) for responsible disclosure.

---

## 🎯 What IS Working Well

To be fair, these parts are solid:

- ✅ **31 analysis tools** — all tested, all deterministic
- ✅ **4 AI agents** — verified in live sessions
- ✅ **REST API (24 endpoints)** — with API key auth
- ✅ **56 unit tests** — 100% pass rate
- ✅ **Zero runtime dependencies for the 31 core tools** — pure Python
- ✅ **Live demo** — works in any browser
- ✅ **Docker + CI/CD** — automated testing and deployment

---

## 📖 When Will These Be Fixed?

See [docs/roadmap.md](docs/roadmap.md) for the full timeline.

**Short answer:** Most limitations require a desktop/laptop environment (Ghidra, Frida, Next.js, LLMs). They are tracked as GitHub Issues so contributors can pick them up.

---

**Last updated:** October 2026
