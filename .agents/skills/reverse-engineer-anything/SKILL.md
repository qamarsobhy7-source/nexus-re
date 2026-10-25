# Skill: Reverse Engineer Anything with NEXUS-RE

> **ℹ️ Note:** This document is for AI agents and contributors. It is **not** part of the NEXUS-RE runtime. See `README.md` for actual capabilities.

> Version: 1.0.0 | Last Updated: 2026-10-16

This skill teaches AI agents how to use NEXUS-RE for reverse engineering and security analysis.

---

## When to Use This Skill

Use this skill when the user asks you to:

- Analyze a binary file (ELF, PE, Mach-O)
- Identify the type of an unknown file
- Detect malware, ransomware, or suspicious code
- Extract indicators of compromise (IOCs)
- Brute-force XOR-encrypted strings
- Compare two versions of a binary
- Analyze a Base64-encoded payload
- Understand what a program does
- Assess the security of a binary

---

## Prerequisites

NEXUS-RE must be available. Verify by running:

python -c "from nexus_re_v3 import calculate_hash; print(calculate_hash('test'))"

If this fails, install NEXUS-RE first. See docs/installation.md.

---

## Workflow

Follow this five-step workflow for every reverse engineering task.

### Step 1: Identify the Target

Ask the user:

- What file do you want to analyze?
- Do you have the file path or a hex string?
- What is your goal? (malware detection, function extraction, version diff, etc.)

### Step 2: Determine the Tool

Use this decision table:

| User Goal | Primary Tool |
|-----------|--------------|
| Unknown file type | detect_file_type_hex |
| General analysis | full_analysis |
| Malware detection | yara_scan + scan_suspicious_apis |
| IOC extraction | extract_iocs |
| Encrypted strings | xor_bruteforce_v2 |
| Compare versions | version_diff |
| Find hidden sections | section_analyzer |
| Decode Base64 | base64_detector |
| String comparison | string_similarity |

### Step 3: Execute the Tool

Call the appropriate function. Example:

from nexus_re_v3 import full_analysis

with open('/path/to/target', 'rb') as f:
    hex_data = f.read().hex()

result = full_analysis(hex_data)
print(result)

### Step 4: Interpret the Evidence

Every result includes:

- tool: which tool produced the result
- result: the raw output
- confidence: HIGH / MEDIUM / LOW
- artifact: hash, offset, or byte range

Explain the evidence to the user in plain language.

### Step 5: Report Limitations

Always mention limitations:

- If the binary is packed, deep analysis may be inaccurate
- If no source code is available, results are approximate
- If a heuristic tool (XOR, Base64) is used, results are not guaranteed

---

## Tool Reference (All 21 Tools)

### Basic Tools

1. hex_dump(text)
   Input: text string
   Output: size in bytes + hex representation

2. extract_strings(text)
   Input: text string
   Output: readable ASCII strings (4+ chars)

3. calculate_hash(text)
   Input: text string
   Output: SHA256 + MD5 digests

4. calculate_entropy(text)
   Input: text string
   Output: Shannon entropy + verdict (LOW / MEDIUM / HIGH)

5. file_info(filename)
   Input: filename
   Output: metadata

6. detect_file_type(text)
   Input: text with magic bytes
   Output: file type + confidence

### Binary Tools

7. detect_file_type_hex(hex_string)
   Input: hex string
   Output: file type + confidence

8. parse_elf_header(hex_string)
   Input: hex string
   Output: ELF class, endianness, architecture, entry point

9. parse_pe_header(hex_string)
   Input: hex string
   Output: PE architecture, sections, flags, timestamp

10. extract_iocs(hex_string)
    Input: hex string
    Output: URLs, IPs, emails, registry keys, file paths

11. xor_bruteforce(hex_string)
    Input: hex string
    Output: Top 5 candidate keys (basic scoring)

12. xor_bruteforce_v2(hex_string)
    Input: hex string
    Output: Top 3 candidate keys (English frequency scoring)

13. scan_suspicious_apis(hex_string)
    Input: hex string
    Output: Threat level + suspicious Windows APIs

14. detect_packer(hex_string)
    Input: hex string
    Output: Packer name (UPX, ASPack, Themida, VMProtect, MPRESS)

15. yara_scan(hex_string)
    Input: hex string
    Output: Matched rules + threat assessment

### Advanced Tools

16. full_analysis(hex_string)
    Input: hex string
    Output: Complete report (6 sections)

17. analyze_file(file_path)
    Input: file path
    Output: Complete report

18. version_diff(hex1, hex2)
    Input: two hex strings
    Output: similarity percentage + first differences

19. section_analyzer(hex_string)
    Input: hex string
    Output: entropy per 1/8 chunk

20. base64_detector(hex_string)
    Input: hex string
    Output: Base64 candidates + decoded text

21. string_similarity(text1, text2)
    Input: two text strings
    Output: 4 similarity metrics + verdict

---

## Multi-Agent Workflow

For comprehensive analysis, use the multi-agent system.

from nexus_agents import Orchestrator
from nexus_re_v3 import full_analysis
import importlib.util

# Load toolkit
spec = importlib.util.spec_from_file_location("nexus_re_v3", "nexus_re_v3.py")
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)

# Run orchestrator
orch = Orchestrator(toolkit)
state = orch.run("/path/to/target")

print(state.final_report)
print(f"Verdict: {state.verdict}")
print(f"Evidence: {len(state.evidence)} pieces")

The orchestrator runs four agents:

1. Static Agent -- file type, ELF/PE parsing, entropy
2. Security Agent -- IOCs, suspicious APIs, packers, YARA
3. Crypto Agent -- XOR brute-force, Base64 detection
4. Report Agent -- evidence synthesis + verdict

---

## RAG Grounding

For grounded reasoning, use the RAG service.

from nexus_rag import RAGService

service = RAGService()
results = service.retrieve("ransomware bitcoin", top_k=3)

for r in results:
    print(r['id'], r['title'], r['severity'])

Knowledge base includes:

- 3 NVD/CVE entries (Log4Shell, Spring4Shell, EternalBlue)
- 5 MITRE ATT&CK techniques (T1055, T1056, T1486, T1071, T1496)
- 2 packer signatures (UPX, Themida)
- 2 RE tool docs (Ghidra headless, Frida hooks)

---

## Example Conversations

### Example 1: Unknown File

User: "What is this file?"

Agent:
1. Call detect_file_type_hex
2. Report the type with confidence
3. Offer to run full_analysis

### Example 2: Malware Detection

User: "Is this file malicious?"

Agent:
1. Call yara_scan (check for ransomware, keylogger, etc.)
2. Call scan_suspicious_apis (check for CreateRemoteThread, etc.)
3. Call detect_packer (check if packed)
4. Report verdict with evidence

### Example 3: Extracting IOCs

User: "Find all indicators of compromise in this binary."

Agent:
1. Call extract_iocs
2. Report URLs, IPs, emails, registry keys
3. Offer to run full_analysis

### Example 4: Version Comparison

User: "What changed between these two versions?"

Agent:
1. Call version_diff with both hex strings
2. Report similarity percentage
3. Report first 10 differences
4. Offer to run full_analysis on both

### Example 5: Multi-Agent Analysis

User: "Give me a full analysis."

Agent:
1. Run Orchestrator with the target
2. Report session ID, verdict, evidence count
3. Output the full report
4. Highlight critical findings

---

## Error Handling

If a tool returns "Invalid hex", the input is not valid hex. Ask the user to provide hex or a file path.

If a tool returns "Data too small", the input is too short. Ask for a larger sample.

If the toolkit fails to load, verify the installation. See docs/installation.md.

---

## Ethical Guidelines

Follow these rules:

1. Only analyze files the user owns or has permission to analyze.
2. Never execute binaries automatically.
3. Run malware analysis in isolated sandboxes.
4. Follow a 90-day responsible disclosure policy.
5. Do not generate working exploits.
6. Report findings responsibly.

---

## Limitations

NEXUS-RE cannot:

- Recover original source code (impossible with any decompiler)
- Predict hidden behavior (only reports evidence)
- Analyze packed binaries deeply without unpacking
- Run dynamic analysis without Frida (planned)
- Replace a human reverse engineer for critical decisions

Always inform the user of these limitations.

---

## Quick Reference Card

Goal: Unknown file
Tool: detect_file_type_hex

Goal: Full analysis
Tool: full_analysis

Goal: Malware check
Tool: yara_scan + scan_suspicious_apis

Goal: IOC extraction
Tool: extract_iocs

Goal: XOR decryption
Tool: xor_bruteforce_v2

Goal: Version compare
Tool: version_diff

Goal: Multi-agent
Tool: Orchestrator.run()

Goal: Grounded reasoning
Tool: RAGService.retrieve()

---

## References

- README.md -- Project overview
- docs/architecture.md -- System architecture
- docs/cli.md -- CLI reference
- docs/evidence.md -- Evidence system
- docs/installation.md -- Installation guide
- docs/roadmap.md -- Development roadmap
- GitHub: https://github.com/qamarsobhy7-source/nexus-re