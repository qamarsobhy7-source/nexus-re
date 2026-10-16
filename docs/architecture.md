# NEXUS-RE Architecture

> Version: 3.0.0 | Last Updated: 2026-10-16

This document describes the architecture of NEXUS-RE, an AI-powered reverse engineering and security analysis platform.

---

## Design Philosophy

NEXUS-RE follows four core principles:

### 1. Orchestration, Not Reinvention

NEXUS-RE does not build its own decompiler or disassembler. Instead, it orchestrates 21 deterministic analysis tools and exposes them to AI agents through a standardized protocol.

### 2. Evidence Before Inference

Every analytical claim produced by NEXUS-RE is accompanied by:

- Evidence: the raw output from the tool
- Confidence: HIGH / MEDIUM / LOW
- Artifact: hash, offset, or byte range
- Timestamp: when the analysis was performed

No black-box answers. Every conclusion must be traceable to a tool's output.

### 3. Local by Design

All analysis runs locally on the user's machine. No binaries are uploaded to any cloud service unless explicitly opted in.

### 4. Modular Composition

Every layer in NEXUS-RE is replaceable. The CLI can be swapped for a web dashboard. The custom orchestrator can be swapped for LangGraph. The TF-IDF RAG can be swapped for FAISS or Chroma.

---

## Five-Layer Architecture

NEXUS-RE is organized as a five-layer architecture.

Layer 1 - Client Layer
- Web Dashboard (index.html)
- CLI (nexus_re_v3.py)
- REST API (api.py)

Layer 2 - API Gateway
- Pure-Python HTTP Server
- CORS support
- 24 endpoints

Layer 3 - Orchestration Layer
- Multi-Agent Orchestrator (nexus_agents.py)
- RAG Service (nexus_rag.py)
- Session Memory

Layer 4 - Tools Layer
- 21 Analysis Tools (nexus_re_v3.py)
- Basic: 6 | Format: 3 | Threat: 4 | Crypto: 2 | Advanced: 6

Layer 5 - Infrastructure Layer
- Docker + Docker Compose
- GitHub Actions CI/CD
- MIT License

---

## Layer 1 -- Client Layer

### 1.1 Web Dashboard

File: index.html

A single-file web application with embedded CSS and JavaScript:

- 21 interactive tool buttons
- Live output panel
- Multi-agent analysis trigger
- RAG query interface

### 1.2 CLI

File: src/tools/nexus_re_v3.py

Interactive menu-driven CLI with 21 tools divided into three categories:

- Basic (6): text-based analysis
- Binary (9): hex-based analysis
- Advanced (6): composite and specialized tools

### 1.3 REST API

File: src/api/api.py

Pure-Python HTTP server exposing 24 endpoints. Uses Python's standard http.server module. No external dependencies.

---

## Layer 2 -- API Gateway

### Endpoints

GET /health - Server status
GET /tools - List all 21 tools
GET /rag/search - RAG knowledge retrieval
POST /hex_dump - Convert text to hex
POST /calculate_hash - SHA256 + MD5
POST /detect_file_type - Magic-number detection
POST /parse_elf - ELF header parsing
POST /parse_pe - PE header parsing
POST /extract_iocs - IOC extraction
POST /xor_bruteforce - XOR brute-force v1
POST /xor_bruteforce_v2 - XOR brute-force v2
POST /scan_apis - Suspicious API scanner
POST /detect_packer - Packer detection
POST /yara_scan - YARA-style matching
POST /full_analysis - Complete report
POST /analyze_file - File-path analysis
POST /version_diff - Binary comparison
POST /section_analyzer - Entropy per section
POST /base64_detector - Base64 detection
POST /string_similarity - 4-metric comparison
POST /agents/analyze - Multi-agent analysis

Total: 24 endpoints.

### CORS Support

Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization

---

## Layer 3 -- Orchestration Layer

### 3.1 Multi-Agent System

File: src/agents/nexus_agents.py

Four specialist agents work in sequence:

[ Orchestrator ]
       |
+------+------+
|      |      |
Static Security Crypto
       |
    Report

Agent Roles:

Static Agent: File type, ELF/PE parsing, entropy
Security Agent: IOCs, suspicious APIs, packers, YARA
Crypto Agent: XOR brute-force, Base64 detection
Report Agent: Evidence synthesis + verdict

### 3.2 Evidence Data Structure

Every evidence item follows this schema:

@dataclass
class Evidence:
    tool: str           # Which tool produced it
    result: str         # What was found
    confidence: str     # HIGH / MEDIUM / LOW
    artifact: str       # hash, offset, or byte range
    timestamp: str      # ISO 8601 format

### 3.3 Session State

Each analysis session maintains a shared AnalysisState:

@dataclass
class AnalysisState:
    target: str
    session_id: str
    evidence: List[Evidence]
    plan: List[str]
    current_step: int
    final_report: str
    verdict: str

### 3.4 RAG Service

File: src/rag/nexus_rag.py

TF-IDF retrieval engine over 12 curated entries:

- 3 NVD/CVE entries: Log4Shell, Spring4Shell, EternalBlue
- 5 MITRE ATT&CK techniques: T1055, T1056, T1486, T1071, T1496
- 2 packer signatures: UPX, Themida
- 2 RE tool docs: Ghidra headless, Frida hooks

---

## Layer 4 -- Tools Layer

File: src/tools/nexus_re_v3.py

21 deterministic analysis tools organized into five categories.

Basic (6): hex_dump, extract_strings, calculate_hash, calculate_entropy, file_info, detect_file_type

Format (3): detect_file_type_hex, parse_elf_header, parse_pe_header

Threat (4): extract_iocs, scan_suspicious_apis, detect_packer, yara_scan

Crypto (2): xor_bruteforce, xor_bruteforce_v2

Advanced (6): version_diff, section_analyzer, base64_detector, string_similarity, full_analysis, analyze_file

### Design Principles

1. Pure functions -- every tool takes input and returns output, no side effects.
2. Deterministic -- same input always produces same output.
3. Zero dependencies -- no external Python packages required.
4. Fast -- all tools complete in less than 100 ms.
5. Testable -- 27 unit tests, 100% pass rate.

---

## Layer 5 -- Infrastructure Layer

### 5.1 Docker

Files: Dockerfile, docker-compose.yml

Multi-stage Docker build with non-root user for security.

### 5.2 CI/CD

File: .github/workflows/ci.yml

GitHub Actions pipeline running on 3 Python versions (3.11, 3.12, 3.13).

### 5.3 License

File: LICENSE

MIT License -- permits commercial use, modification, and distribution.

---

## Data Flow (End-to-End)

[ User Input ]
      |
      v
[ CLI / Web / API ]
      |
      v
[ Orchestrator plans agents ]
      |
      v
[ Static Agent -> Security Agent -> Crypto Agent ]
      |
      v
[ RAG Service grounds findings in CVE + ATT&CK ]
      |
      v
[ Report Agent synthesizes ]
      |
      v
[ Output: Text report + Evidence ledger (JSON) ]

---

## Comparison with REA

Language: NEXUS-RE Python, REA TypeScript/Node.js
Tools: NEXUS-RE 21, REA 207
Providers: NEXUS-RE 0, REA 26
Agents: NEXUS-RE 4, REA 0
RAG: NEXUS-RE TF-IDF, REA No
Multi-Agent: NEXUS-RE Yes, REA No
Web App: NEXUS-RE Yes, REA No
REST API: NEXUS-RE Yes, REA No
Focus: NEXUS-RE Static + Threat, REA Native + Dynamic

---

## Future Work

- Phase 5: Real LangGraph orchestrator (replacing custom one)
- Phase 6: Ghidra, Frida, JADX, radare2 integration
- Phase 7: LLM integration (Llama 3, Mistral, Jais)
- Phase 8: Live demo on Hugging Face Spaces

---

## References

- NIST SP 800-218 -- Secure Software Development Framework
- Model Context Protocol -- https://modelcontextprotocol.io
- Mitchell et al. (2019) -- Model Cards for Model Reporting