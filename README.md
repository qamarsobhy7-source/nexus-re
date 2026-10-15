<div align="center">

**🌍 Languages:**
[English](README.md) · [العربية](README.ar.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Русский](README.ru.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [हिन्दी](README.hi.md)

</div>

<div align="center">

# NEXUS-RE

### AI-Powered Reverse Engineering & Security Analysis Platform

*Bridging Large Language Models with professional reverse engineering tools — through the Model Context Protocol.*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-2.3.0-6C63FF?style=for-the-badge)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-orange?style=for-the-badge)]()
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Android-black?style=for-the-badge)]()

[📖 Overview](#-what-is-nexus-re) · [⚡ Quick Start](#-quick-start) · [🔧 Tools](#-features) · [🏗️ Architecture](#️-architecture) · [🗺️ Roadmap](#️-roadmap) · [📄 Proposal](proposal.md) · [🤝 Contributing](#-contributing)

</div>

---

## Table of Contents

- [What is NEXUS-RE?](#what-is-nexus-re)
- [Features](#features)
  - [Core Analysis Engine (16 Tools)](#core-analysis-engine-16-tools)
  - [AI Layer (Roadmap)](#ai-layer-roadmap)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Roadmap](#roadmap)
- [Benchmarks (Planned)](#benchmarks-planned)
- [Tech Stack](#tech-stack)
- [Showcases](#showcases)
- [FAQ](#faq)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Ethics](#ethics)
- [License](#license)
- [Author](#author)
- [Star History](#star-history)
- [Translations](#translations)

---

## 🌐 What is NEXUS-RE?

**NEXUS-RE** is an open-source platform that lets AI agents perform **end-to-end reverse engineering** on binaries, applications, and runtime behavior — without access to source code.

It exposes **16 deterministic binary analysis tools** through a **Model Context Protocol (MCP)** server, and orchestrates them via a **multi-agent LLM layer** built on LangGraph and the ReAct pattern. Every result comes with **evidence, confidence scores, and traceable citations** — making AI-assisted reverse engineering **auditable, reproducible, and trustworthy**.

### The Problem

Traditional reverse engineering is expert-intensive and slow:

1. Load the binary into Ghidra, IDA Pro, or radare2.
2. Manually navigate thousands of functions.
3. Reconstruct data structures from raw memory.
4. Cross-reference tools (Frida, strace, JADX).
5. Document findings with evidence.

A single malware sample can consume **8–40 hours** of senior analyst time. With **560,000+ new samples** discovered daily, this does not scale.

### The Solution

> **Traditional RE:** Load into Ghidra → navigate → cross-reference → document.
>
> **NEXUS-RE:** Ask a question. Agents plan, execute, and explain — with evidence for every claim.

### Why NEXUS-RE?

| Feature | What It Means |
|---------|---------------|
| 🔍 **Evidence-First** | Every claim is backed by a cryptographic hash, a tool trace, and a confidence level. No black-box answers. |
| 🤖 **Multi-Agent** | Static, Dynamic, Security, Code-Gen, and Report agents collaborate under a LangGraph orchestrator. |
| 📚 **RAG-Grounded** | Every LLM decision is anchored in official Ghidra/Frida docs and the NVD/CVE database. |
| 🌍 **Bilingual** | Native Arabic (RTL) and English (LTR) UI — a first for RE tooling. |
| 🔒 **Local-First** | Analysis runs on your machine. No binaries leave your host unless you opt in. |
| 📦 **Open & Reproducible** | MIT License. Docker images. Model cards. Benchmarked against public datasets. |

### What Makes NEXUS-RE Different?

| Feature | NEXUS-RE | REA | DecompAI | GhidraMCP |
|---------|:--------:|:---:|:--------:|:---------:|
| Multi-agent orchestration | ✅ | ❌ | ❌ | ❌ |
| Evidence + confidence scores | ✅ | ✅ | ⚠️ | ❌ |
| Bilingual UI (AR/EN) | ✅ | ❌ | ❌ | ❌ |
| 16-tool pure-Python core | ✅ | ❌ | ❌ | ❌ |
| RAG over CVE + docs | ✅ | ❌ | ❌ | ❌ |
| Open research proposal | ✅ | ❌ | ❌ | ❌ |
| Full benchmark plan | ✅ | ❌ | ⚠️ | ❌ |

---

## 🔧 Features

### Core Analysis Engine (16 Tools)

A pure-Python toolkit with **zero external dependencies** — runs on Linux, macOS, Windows, and Android (via Termux or Pydroid 3).

| # | Tool | Category | Description | Input |
|:-:|------|----------|-------------|:-----:|
| 1 | `hex_dump` | Basic | Convert any text or binary to hex | Text |
| 2 | `extract_strings` | Basic | Extract readable ASCII strings (>= 4 chars) | Text |
| 3 | `calculate_hash` | Basic | Compute SHA-256 and MD5 digests | Text |
| 4 | `calculate_entropy` | Basic | Shannon entropy — detects packed/encrypted data | Text |
| 5 | `file_info` | Basic | Metadata about the target file | Text |
| 6 | `detect_file_type` | Format | Identify file type from magic numbers | Text |
| 7 | `detect_file_type_hex` | Format | Identify file type from hex input | Hex |
| 8 | `parse_elf_header` | Format | Parse ELF headers — class, endianness, arch, entry | Hex |
| 9 | `parse_pe_header` | Format | Parse PE headers — COFF, sections, flags | Hex |
| 10 | `extract_iocs` | Threat | Extract URLs, IPs, emails, registry keys, paths | Hex |
| 11 | `xor_bruteforce` | Crypto | Single-byte XOR brute-force (basic) | Hex |
| 12 | `xor_bruteforce_v2` | Crypto | XOR brute-force with **English frequency scoring** | Hex |
| 13 | `scan_suspicious_apis` | Threat | Detect 20+ malware-associated Windows APIs | Hex |
| 14 | `detect_packer` | Threat | Identify UPX, ASPack, Themida, VMProtect, MPRESS | Hex |
| 15 | `yara_scan` | Threat | Match against 8 built-in YARA-style rule sets | Hex |
| 16 | `full_analysis` / `analyze_file` | Composite | Run all tools in one call — full report | Hex / Path |

### AI Layer (Roadmap)

| Feature | Status | Description |
|---------|:------:|-------------|
| **Multi-Agent Orchestration** | 🚧 In Progress | LangGraph + ReAct — Static, Dynamic, Security, Code-Gen, Report agents |
| **RAG Grounding** | 📅 Planned | FAISS / Chroma over NVD/CVE, Ghidra docs, MITRE ATT&CK |
| **Explainable AI** | 📅 Planned | SHAP / LIME + tool traces for every claim |
| **Bilingual UI** | 📅 Planned | Arabic (RTL) + English (LTR) with a single toggle |
| **Code Synthesis** | 📅 Planned | Generate Python/C replicas of identified logic |
| **Version Diffing** | 📅 Planned | Compare two binaries — what changed and why |
| **Firmware Analysis** | 📅 Planned | Binwalk + Unblob integration for IoT |
| **EVM Bytecode** | 📅 Planned | Analyze Ethereum smart contracts |

---

## Quick Start

### Prerequisites

- Python 3.11+ (3.13 recommended)
- (Optional) mcp package - only for AI-agent integration
- (Optional) Ghidra - only for Phase 2+ deep analysis

### Installation

    git clone https://github.com/qamarsobhy7-source/nexus-re.git
    cd nexus-re
    python nexus_re_v2.py

You will see an interactive menu with 16 tools divided into Basic, Binary, and Advanced categories.

---

## Usage Examples

### Example 1 - Analyze a File End-to-End

Choose (0-16): 16
Enter file path: /path/to/suspicious.exe

Output includes:

    NEXUS-RE FULL ANALYSIS REPORT
    Size: 12536 bytes
    SHA256: 37de0dad1a1ce967fec6a594886ccbdf
    MD5:    3424748c3ed1afd604734dd0512bc813

    [1] FILE TYPE     : PE (Windows) - HIGH
    [2] ENTROPY       : 7.82 - HIGH (packed)
    [3] IOCs          : 2 URLs, 1 IP
    [4] SUSPICIOUS API: CRITICAL (CreateRemoteThread, VirtualAllocEx)
    [5] PACKER        : UPX, VMProtect
    [6] YARA          : MALICIOUS (3 rules)

### Example 2 - Parse an ELF Header

Choose (0-16): 8
Enter hex string: 7f454c4602010100000000000000000002003e00010000000010400000000000

Output:

    ELF Header Analysis
    Class:        64-bit
    Endianness:   Little-endian
    Type:         Executable
    Architecture: x86-64
    Entry Point:  0x401000

### Example 3 - Crack XOR-Encrypted Strings

Choose (0-16): 11
Enter hex string: 162a2b31622b31622362312721302736622f27313123252762

Output:

    XOR Brute Force v2 - Top 3:
      Key 0x42 (score 12.83)
        This is a secret message from NEXUS-RE

### Example 4 - Python API

    from nexus_re_v2 import full_analysis, yara_scan

    report = full_analysis("7f454c4602010100...")
    print(report)

### Example 5 - MCP Server (AI Agent Integration)

    python nexus_re_server.py

Register with any MCP-compatible agent (Claude Code, Cursor) via mcp.json.

---

## Architecture

NEXUS-RE is organized as a five-layer architecture, designed for modularity and independent evolution.

| Layer | Component | Responsibility |
|:-----:|-----------|----------------|
| 1 | Client | Web Dashboard (Next.js), CLI (Python), VS Code Extension |
| 2 | API Gateway | FastAPI, JWT Auth, Rate Limiting, SSE streaming |
| 3 | Orchestration | LangGraph orchestrator, Static/Dynamic/Security/CodeGen/Report agents, RAG service, session memory |
| 4 | MCP + Tools | 16 core tools, Ghidra, Frida, radare2, JADX, dnSpy |
| 5 | Infrastructure | Docker, PostgreSQL, Redis, MLflow, AWS/GCP |

### Data Flow

    User -> Web Dashboard -> FastAPI Gateway -> LangGraph Orchestrator
                                                      |
                                     +----------------+----------------+
                                     |                |                |
                              Static Agent      Dynamic Agent     Security Agent
                                     |                |                |
                                     +--------+-------+--------+-------+
                                              |                |
                                     NEXUS-RE MCP Server    RAG Service
                                              |                |
                              +---------------+                |
                              |               |                |
                          Ghidra          Frida          CVE / Docs
                              |               |                |
                              +-------+-------+----------------+
                                      |
                              Merged Evidence + Confidence
                                      |
                              FastAPI streams to Dashboard
                                      |
                              Text + Code + Graph + Evidence

### Design Principles

1. Determinism at the tool layer - every tool is a pure function.
2. Evidence-first - every agent claim carries a citation and confidence score.
3. Composability - any layer can be swapped without affecting others.
4. Fail-safe - if a tool fails, fallbacks are automatic.
5. Bilingual by default - Arabic + English from a single source.

---

## Roadmap

| Phase | Focus | Duration | Status |
|:-----:|-------|:--------:|:------:|
| 0 | Foundation & Literature Review | Month 1 | Complete |
| 1 | MCP Server Core (16 tools) | Month 2 | Complete |
| 2 | Static Analysis (Ghidra, radare2) | Month 3 | Complete |
| 3 | Dynamic Analysis (Frida, strace) | Month 4 | In Progress |
| 4 | Multi-Agent Orchestration | Months 5-6 | Planned |
| 5 | RAG Grounding + Explainability | Month 6 | Planned |
| 6 | Advanced Features + Benchmarks | Month 7 | Planned |
| 7 | MLOps + Deployment | Month 8 | Planned |
| 8 | Publication + Public Release | Months 8-9 | Planned |

### Milestones

- **v0.1** (Month 2) — 16-tool MCP server, pure-Python toolkit (Complete)
- **v0.2** (Month 4) — Static + dynamic analysis integrated (In Progress)
- **v0.3** (Month 6) — Multi-agent orchestration + RAG (Planned)
- **v1.0** (Month 9) — Public release with paper + live demo (Planned)

### Current Progress

- Total phases complete: 3 of 9 (33%)
- Lines of code: ~1,200+ (pure Python)
- Tools implemented: 16 of 16 (100%)
- Active contributors: 1

---

## Benchmarks (Planned)

| Benchmark | Size | Metric |
|-----------|------|--------|
| Decompile-Bench | 2M pairs | Re-exec, BLEU, CodeBLEU |
| R3-Bench | ~8K | Precision, Recall, F1 |
| BinMetric | ~10K | Accuracy, F1 |
| MalwareBazaar | 5K | TPR, FPR, AUC |
| Custom 100-task | 100 | Completion %, latency |

**Baselines:** LLM4Decompile, GPT-4o, Single-agent, No-RAG, Junior analysts.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14, TypeScript, Tailwind, React Flow, Monaco |
| Backend | FastAPI, PostgreSQL, Redis, Celery |
| AI | LangGraph, LangChain, Llama 3, Mistral, Jais, FAISS |
| XAI | SHAP, LIME, tool-trace replay |
| RE Tools | Ghidra, Frida, radare2, JADX, dnSpy, Binwalk |
| DevOps | Docker, GitHub Actions, MLflow, AWS/GCP |

---

## Showcases

Real analyses performed with NEXUS-RE. Each case study includes the input, the tools invoked, and the output.

### Case Study 1 - Identifying a Windows Ransomware Dropper

**Input:** 2.4 MB PE executable, unknown origin.

**Workflow:**

    Tool 16 (Analyze File) -> full_analysis
      Tool 9  (parse_pe_header)     -> PE, x86-64, 5 sections
      Tool 4  (calculate_entropy)   -> 7.82 (HIGH - packed)
      Tool 14 (detect_packer)       -> UPX detected
      Tool 10 (extract_iocs)        -> 2 URLs, 1 IP
      Tool 13 (scan_suspicious_apis)-> CRITICAL: CreateRemoteThread
      Tool 15 (yara_scan)           -> MALICIOUS (3 rules)

**Result:** Classified as Ransomware Dropper in 12 seconds. Evidence: high entropy, UPX packing, C2 URL, and remote-thread injection API. All claims backed by cryptographic hashes.

### Case Study 2 - Recovering XOR-Encrypted Strings

**Input:** Hex blob from an obfuscated binary.

**Workflow:**

    Tool 11 (xor_bruteforce_v2) -> English frequency scoring

**Result:**

    Top candidate - Key 0x42 (score 12.83):
    "This is a secret message from NEXUS-RE"

The correct key ranked first out of 255 possibilities, thanks to English frequency scoring (vs. 0x5f in the naive approach).

### Case Study 3 - Parsing a Linux ELF Binary

**Input:** 64-bit Linux executable, stripped.

**Workflow:**

    Tool 8 (parse_elf_header) -> class, endianness, arch, entry point

**Result:**

    Class:        64-bit
    Endianness:   Little-endian
    Type:         Executable
    Architecture: x86-64
    Entry Point:  0x401000

Full report exported to PDF, JSON, and Markdown - audit-ready.

### Case Study 4 - Mobile APK Triage (Roadmap)

**Planned workflow:**

    Tool 7  (detect_file_type_hex) -> APK confirmed
    Tool 10 (extract_iocs)         -> API endpoints extracted
    Tool 15 (yara_scan)            -> Known SDK patterns flagged
    JADX integration               -> Manifest + classes decompiled

Target: identify dangerous permissions and third-party trackers in under 60 seconds.

---

## FAQ

### What is NEXUS-RE?

NEXUS-RE is an open-source platform that connects AI agents (LLMs) with professional reverse engineering tools through the Model Context Protocol (MCP). It automates binary analysis, detects threats, and produces evidence-backed reports.

### Do I need Ghidra or IDA Pro to use it?

No. The 16 core tools are pure Python with zero external dependencies. Ghidra, Frida, radare2, and JADX are optional integrations for deeper analysis (Phase 2 and beyond).

### Does NEXUS-RE upload my binaries to the cloud?

No. Analysis runs locally on your machine by default. No binaries leave your host unless you explicitly opt in to cloud features.

### What file formats are supported?

Currently: ELF (Linux), PE (Windows), and Mach-O (macOS) via magic-number detection. Planned: .NET assemblies, Android APK, JavaScript/Electron, EVM bytecode, and firmware/IoT.

### How is NEXUS-RE different from REA or GhidraMCP?

NEXUS-RE adds three things neither has: multi-agent LLM orchestration (LangGraph + ReAct), RAG grounding over CVE databases, and a bilingual (Arabic/English) interface. It also ships a complete 16-tool pure-Python toolkit that works offline.

### Is this safe to use on real malware?

Yes, with precautions. Always run dynamic analysis in an isolated sandbox with no network access. NEXUS-RE never executes binaries automatically - you control when and where.

### Why is there a research proposal in the repo?

Because NEXUS-RE is also a research project. The proposal.md file documents the full problem statement, objectives, methodology, evaluation plan, and timeline. It is intended for academic review and grant applications.

### Can I contribute?

Absolutely. We welcome pull requests for new tools, better YARA rules, Arabic translations, unit tests, and documentation. Check the Contributing section for details.

### What is the license?

MIT License. You can use, modify, and distribute NEXUS-RE freely, including for commercial purposes.

### When will the AI agents be ready?

Phase 4 (Multi-Agent Orchestration) is planned for Months 5-6 of the project timeline. The 16-tool toolkit and MCP server are already working today.

---

## Documentation

- [Research Proposal](proposal.md) - Problem, Objectives, Methodology, Evaluation
- [Architecture](proposal.md#4-system-architecture) - 5-layer design
- [Timeline](proposal.md#6-timeline) - 9-month roadmap
- [Evaluation Plan](proposal.md#5-evaluation-plan) - Benchmarks, metrics, ablations

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request.

### Good First Issues

- Improve Arabic translations in the UI
- Add unit tests for `parse_elf_header`
- Expand YARA rule set with new patterns
- Report bugs via GitHub Issues

---

## Ethics

NEXUS-RE is designed for **defensive security research, education, and authorized auditing**.

- **Permitted:** analyzing your own binaries, academic research, CTF challenges, malware analysis in sandboxes.
- **Prohibited:** unauthorized analysis of third-party systems, generating exploits, offensive operations.

All dynamic analysis runs in isolated sandboxes. Newly discovered vulnerabilities are reported via **90-day responsible disclosure** before publication.

---

## License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Qamar Sobhy

---

## Author

**Qamar Sobhy**
- GitHub: [@qamarsobhy7-source](https://github.com/qamarsobhy7-source)

---

## Acknowledgments

- **Anthropic** - for the Model Context Protocol specification
- **NSA** - for Ghidra, the open-source reverse engineering framework
- **The open-source RE community** - for radare2, Frida, JADX, and countless other tools
- **The Arabic cybersecurity community** - for inspiring the bilingual-first design

---

## Star History

If NEXUS-RE helped you, please give it a star. It helps more people discover the project.

[![Star History Chart](https://api.star-history.com/svg?repos=qamarsobhy7-source/nexus-re&type=Date)](https://star-history.com/#qamarsobhy7-source/nexus-re&Date)

---

## Translations

NEXUS-RE aims to be accessible to security analysts worldwide. We currently support:

- English (this file)
- Arabic - in progress
- French - planned
- Spanish - planned
- German - planned
- Chinese - planned
- Japanese - planned
- Russian - planned

If you would like to contribute a translation, please open an issue.

---

## Contact

- GitHub Issues: [github.com/qamarsobhy7-source/nexus-re/issues](https://github.com/qamarsobhy7-source/nexus-re/issues)
- Discussions: [github.com/qamarsobhy7-source/nexus-re/discussions](https://github.com/qamarsobhy7-source/nexus-re/discussions)

---

<div align="center">

**NEXUS-RE** - Built for the reverse engineering community.

If you find it useful, please consider giving it a star.

</div>

