# NEXUS-RE: Building an AI-Ready Reverse Engineering Platform on a Mobile Phone


---

## Abstract

This report documents the design, implementation, and evaluation of NEXUS-RE, an open-source AI-powered reverse engineering platform. Unlike traditional tools that require desktop environments and extensive toolchains, NEXUS-RE was built entirely on an Android phone using Pydroid 3 and Termux. The system exposes 31 deterministic binary analysis tools through a Model Context Protocol (MCP) server, orchestrates them via a custom multi-agent system (Static, Security, Crypto, Report), and grounds findings in a curated RAG knowledge base of 12 entries. The platform is deployed as a live web dashboard on Hugging Face Spaces, backed by a pure-Python REST API. This report shares the engineering decisions, the challenges encountered (including platform bans, dependency hell, and mobile memory limits), and the lessons learned from building a production-grade AI system under severe constraints.

---

## 1. Introduction: Why I Built This

Reverse engineering is the art of understanding software without its source code. For security researchers, it is essential for analyzing malware, discovering vulnerabilities, and auditing third-party binaries. However, the modern RE workflow is extremely fragmented. An analyst typically loads a binary into Ghidra, manually navigates thousands of functions, cross-references findings with Frida for dynamic behavior, checks IOCs against threat intelligence platforms, and finally writes a report in a separate document.

I have seen this workflow firsthand. A single malware sample can consume 8 to 40 hours of a senior analyst's time. With over 560,000 new samples discovered daily, this manual approach is no longer sustainable.

I decided to build NEXUS-RE for three reasons:

1. **To automate the routine.** Many RE tasks (identifying file types, extracting strings, detecting packers, matching YARA rules) are deterministic and can be fully automated.
2. **To explore Multi-Agent AI.** I wanted to test whether specialized AI agents could collaborate on a complex investigation, each bringing its own toolset.
3. **To prove a point.** I wanted to show that a full-stack AI platform—complete with a backend, frontend, API, tests, and documentation—can be built on a mobile phone.

This report is the story of that journey.

---

## 2. Problem Statement

### 2.1 The Reverse Engineering Bottleneck

Traditional RE tools (Ghidra, IDA Pro, radare2) are powerful but demand deep expertise. They are designed for desktop environments with high memory and CPU. The output they produce is raw: pseudocode, assembly listings, and call graphs. Turning this raw output into actionable intelligence requires a human expert who understands both the binary and the threat landscape.

### 2.2 Fragmentation Across Tools

Even for an expert, the workflow is fragmented. Ghidra handles static analysis. Frida handles dynamic analysis. YARA handles pattern matching. VirusTotal handles threat intelligence. None of these tools communicate with each other. The analyst becomes the integration layer, manually copying data from one tool to another.

### 2.3 The AI Opportunity

Large Language Models (LLMs) have demonstrated remarkable capabilities in code comprehension. Early research such as LLM4Decompile and ReSym showed that LLMs can assist with decompilation and variable-name recovery. However, most of these projects are isolated research prototypes. They do not integrate with the professional tools that analysts actually use.

---

## 3. Vision and Design Goals

Before writing a single line of code, I defined four design goals:

1. **Evidence-First.** Every finding must be traceable to a specific tool, a specific artifact (hash, offset, byte range), and a specific timestamp. No black-box answers.
2. **Modular.** Each tool must be a pure Python function. Each agent must be independently testable. The API must be replaceable.
3. **Offline-First.** The core tools must run without internet access. No cloud dependency is acceptable.
4. **Mobile-Compatible.** The entire stack must run on a mid-range Android device with less than 4 GB of RAM.

These goals shaped every architectural decision that followed.

---

## 4. System Architecture

NEXUS-RE is organized into five layers.

### 4.1 Layer 1: Client Layer

The client layer consists of three components:

- **Web Dashboard (`index.html`):** A single-file HTML application with Tailwind CSS, Prism.js for code highlighting, and jsPDF for report export. The dashboard communicates with the API and presents results in three panels: an Evidence Table, Vulnerability Cards, and a Code Viewer.
- **Command-Line Interface (`nexus_re_v3.py`):** A menu-driven CLI exposing all 31 tools. This was the first interface I built and remains the primary way to use NEXUS-RE offline.
- **REST API Client:** Any HTTP client can interact with the API using standard JSON requests.

### 4.2 Layer 2: API Gateway

The API gateway is built on Python's standard `http.server` module. I deliberately avoided FastAPI because its dependency on `pydantic-core` (which requires Rust) made installation on Pydroid 3 impossible. Instead, I wrote a lightweight HTTP server that handles:

- CORS headers for cross-origin requests
- JSON request parsing
- 24 endpoints covering all tools, agents, and RAG functionality

This decision is documented in `api_render.py`.

### 4.3 Layer 3: Orchestration Layer

The orchestration layer is the heart of NEXUS-RE. It consists of:

- **Multi-Agent System (`nexus_agents.py`):** Four specialist agents (Static, Security, Crypto, Report) share an `AnalysisState` object. Each agent reads the state, executes its tools, appends structured `Evidence` objects, and passes the state to the next agent. This is a simplified version of the ReAct pattern.
- **RAG Service (`nexus_rag.py`):** A TF-IDF retrieval engine over 12 curated knowledge entries. The entries cover CVE vulnerabilities (Log4Shell, Spring4Shell, EternalBlue), MITRE ATT&CK techniques (T1055, T1056, T1486, T1071, T1496), packer signatures (UPX, Themida), and RE tool documentation (Ghidra, Frida).

### 4.4 Layer 4: Tools Layer

The tools layer is the foundation. It contains 31 pure-Python functions organized into five categories:

- **Basic (6):** hex_dump, extract_strings, calculate_hash, calculate_entropy, file_info, detect_file_type
- **Format (3):** detect_file_type_hex, parse_elf_header, parse_pe_header
- **Threat (4):** extract_iocs, scan_suspicious_apis, detect_packer, yara_scan
- **Crypto (2):** xor_bruteforce, xor_bruteforce_v2
- **Advanced (16):** version_diff, section_analyzer, base64_detector, string_similarity, pe_section_analyzer, elf_section_analyzer, import_table_parser, export_table_parser, anti_debug_detector, crypto_constant_scanner, string_obfuscation_detector, apk_manifest_parser, certificate_extractor, deep_packer_scanner, full_analysis, analyze_file

Every tool follows the same contract: takes a string (text or hex), returns a string (formatted report). This makes them easy to compose and easy to test.

### 4.5 Layer 5: Infrastructure Layer

The infrastructure layer includes:

- **Docker:** A multi-stage Dockerfile with a non-root user for security.
- **CI/CD:** A GitHub Actions pipeline that runs doctor.py, unit tests on Python 3.11/3.12/3.13, linting with flake8 and black, security scanning with Bandit, and Docker image build.
- **License:** MIT License.

---

## 5. Implementation Journey

### 5.1 The First Attempt: Google Colab

My first instinct was to use Google Colab. It offered a free Python environment with persistent storage on Google Drive. I spent over two weeks building the initial 10 tools there. Then Colab banned my account. The reason: my code contained strings like `CreateRemoteThread` and `VirtualAllocEx`. These are legitimate API names used in malware analysis, but Colab's automated abuse detection flagged them as malicious. I lost access to the runtime. This was a painful lesson. I realized that any AI-assisted security tool must be careful about the platforms it runs on.

### 5.2 The Second Attempt: Termux

I moved to Termux, a full Linux emulator for Android. Termux allowed me to install Python, Rust, and the MCP SDK. I rebuilt the core tools there and reached 16 tools. However, Termux's CLI was extremely difficult to use on a phone keyboard. I could not inspect output easily, and long scripts were prone to errors.

### 5.3 The Third Attempt: Pydroid 3

Pydroid 3 offered a friendly GUI editor with syntax highlighting and a run button. I rebuilt the toolkit there and expanded it to 31 tools. This is where the project finally found its home. Pydroid 3 had its own challenges: No Rust for some dependencies (solved by pinning older versions), Memory limits (solved by splitting code), and No Node.js (solved by using static HTML with CDNs).

### 5.4 Deployment: From Render to Hugging Face

My first deployment target was Render. I configured a `render.yaml` and prepared the API. But Render required a credit card even for the free tier. I moved to Hugging Face Spaces. The platform initially required a PRO subscription for Docker Spaces, but Static Spaces remained free. Since my dashboard was a static HTML file, this was perfect. One subtle issue: Hugging Face's direct URL returned a 404. The correct URL is `*.static.hf.space`. I documented this in the README.

### 5.5 Documentation

I spent as much time on documentation as on code. The project includes a 1,464-line README, an Arabic README, a 630-line proposal, 7 docs files, a 366-line SKILL.md, and a CITATION.cff.

---

## 6. Evaluation

### 6.1 Unit Testing

I wrote 27 unit tests covering all tool categories. Results: 27/27 tests pass (100%).

### 6.2 Multi-Agent Verification

I ran the multi-agent system on a synthetic ELF binary. The orchestrator produced a plan (static -> security -> crypto -> report), executed 4 steps, collected 6 pieces of evidence, and returned a verdict. This demonstrates that the agents collaborate correctly.

### 6.3 RAG Verification

I queried the RAG service with "ransomware bitcoin". The top result was `MITRE-T1486` (Data Encrypted for Impact), which is the correct MITRE technique for ransomware.

### 6.4 API Verification

The API exposes 24 endpoints. I tested the `/health`, `/tools`, and `/full_analysis` endpoints. All tests passed.

### 6.5 Environment Verification

I wrote a `doctor.py` script that checks Python version, required files, module imports, network, and storage. It reports "All critical checks passed" on a fresh installation.

---

## 7. Challenges and Lessons Learned

1. **Platform Bans:** Google Colab banned my account because of security-related strings. Lesson: always be aware of abuse detection policies.
2. **Dependency Hell:** Installing fastapi and huggingface_hub failed due to missing Rust. Lesson: pin older versions or use pure-Python alternatives.
3. **Mobile Memory Limits:** Pydroid 3 crashed with large files. Lesson: split code into modules.
4. **Cloud Deployment Friction:** Render required a credit card. Lesson: research free tiers.
5. **The 404 Mystery:** Hugging Face's direct URL returned 404 until I found `.static.hf.space`.

---

## 8. Limitations

I want to be transparent:
1. No native tool integration (Ghidra, Frida).
2. No real LLM (rule-based agents only).
3. No Next.js dashboard (static HTML only).
4. No decompilation.
5. No dynamic analysis.

These limitations are documented in the README.

---

## 9. Future Work

- v2.0 (Next 6 months): LangGraph, Ghidra Headless, Frida.
- v3.0 (Next 12 months): Next.js dashboard, Monaco Editor, React Flow, SHAP/LIME.
- Publication: Submit a paper to an AI/cybersecurity workshop.

---

## 10. Conclusion

Building NEXUS-RE on a mobile phone was one of the hardest engineering challenges I have faced. Every dependency, every platform, and every tool was designed for a desktop environment. But by carefully choosing pure-Python implementations, testing on real hardware, and documenting every decision, I produced a system that is functional, tested, and deployed. With enough ingenuity, a constrained environment can produce meaningful software.

---

## 11. Acknowledgments

I would like to thank the open-source community behind Ghidra, Frida, radare2, and JADX for the tools that inspired this work. Anthropic for the Model Context Protocol. The Pydroid 3 team for creating a mobile IDE that actually works. Hugging Face for free static hosting.

---

## 12. References

1. Altman, E., et al. (2024). LLM4Decompile. arXiv:2403.05286.
2. Anthropic. (2024). Model Context Protocol. https://modelcontextprotocol.io
3. Yao, S., et al. (2023). ReAct. ICLR 2023.
4. Lewis, P., et al. (2020). RAG. NeurIPS 2020.
5. NIST. (2024). NVD. https://nvd.nist.gov
6. MITRE. (2024). ATT&CK. https://attack.mitre.org
7. Mitchell, M., et al. (2019). Model Cards. FAT* 2019.
