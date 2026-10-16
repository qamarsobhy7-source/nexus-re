# NEXUS-RE Evidence System

> Version: 3.0.0 | Last Updated: 2026-10-16

This document describes how NEXUS-RE collects, structures, and reports evidence. Every analytical claim must be traceable to a tool's output.

---

## Philosophy

REA popularized the concept of Evidence Contracts for reverse engineering. NEXUS-RE adopts the same philosophy:

No black-box answers. Every claim must be backed by evidence.

This means:

1. Every tool returns structured evidence.
2. Every agent claim is traceable to a tool.
3. Every conclusion includes a confidence score.
4. Every result includes its limitations.

---

## Evidence Data Structure

Every evidence item follows this schema:

class Evidence:
    tool: str           # Which tool produced this evidence
    result: str         # What was found (raw output)
    confidence: str     # HIGH / MEDIUM / LOW
    artifact: str       # hash, offset, or byte range
    timestamp: str      # ISO 8601 format

---

## Confidence Levels

Confidence levels are assigned based on tool reliability and evidence clarity.

| Level | Meaning | When Used |
|-------|---------|-----------|
| HIGH | Evidence is deterministic and unambiguous | File type, hash, entropy, magic numbers |
| MEDIUM | Evidence is heuristic but reliable | XOR brute-force, Base64 detection |
| LOW | Evidence is inconclusive | Partial matches, unknown formats |

---

## Tool-to-Confidence Mapping

| Tool | Default Confidence | Reason |
|------|:------------------:|--------|
| hex_dump | HIGH | Deterministic |
| extract_strings | HIGH | Deterministic |
| calculate_hash | HIGH | Deterministic |
| calculate_entropy | HIGH | Deterministic |
| file_info | HIGH | Deterministic |
| detect_file_type | HIGH | Magic-number based |
| detect_file_type_hex | HIGH | Magic-number based |
| parse_elf_header | HIGH | Struct-based parsing |
| parse_pe_header | HIGH | Struct-based parsing |
| extract_iocs | HIGH | Regex-based extraction |
| xor_bruteforce | MEDIUM | Heuristic scoring |
| xor_bruteforce_v2 | MEDIUM | Frequency-based scoring |
| scan_suspicious_apis | HIGH | Signature matching |
| detect_packer | HIGH | Signature matching |
| yara_scan | HIGH | Rule-based matching |
| full_analysis | HIGH | Aggregated from above |
| analyze_file | HIGH | Aggregated from above |
| version_diff | HIGH | Byte-by-byte comparison |
| section_analyzer | HIGH | Math-based entropy |
| base64_detector | MEDIUM | Heuristic pattern match |
| string_similarity | HIGH | Deterministic metrics |

---

## Evidence Ledger

Every analysis session produces an Evidence Ledger. This is a JSON structure containing all evidence items.

Example session (20261016_122358):

{
  "session_id": "20261016_122358",
  "target": "7f454c4602010100000000000000000048656c6c6f204e455855532d5245",
  "evidence": [
    {
      "tool": "detect_file_type_hex",
      "result": "Type: ELF (Linux)\nConfidence: HIGH",
      "confidence": "HIGH",
      "artifact": "magic:7f454c46",
      "timestamp": "2026-10-16T12:23:58"
    },
    {
      "tool": "calculate_entropy",
      "result": "Entropy: 3.6641\nVerdict: LOW (normal)",
      "confidence": "HIGH",
      "artifact": "size:38",
      "timestamp": "2026-10-16T12:23:58"
    },
    {
      "tool": "parse_elf_header",
      "result": "Class: 64-bit\nArchitecture: x86-64",
      "confidence": "HIGH",
      "artifact": "entry:0x401000",
      "timestamp": "2026-10-16T12:23:58"
    },
    {
      "tool": "detect_packer",
      "result": "PACKED: NO",
      "confidence": "HIGH",
      "artifact": "signatures:none",
      "timestamp": "2026-10-16T12:23:58"
    },
    {
      "tool": "yara_scan",
      "result": "YARA: Clean",
      "confidence": "HIGH",
      "artifact": "rules:8",
      "timestamp": "2026-10-16T12:23:58"
    },
    {
      "tool": "xor_bruteforce_v2",
      "result": "Key 0x20 (score 12.9)",
      "confidence": "MEDIUM",
      "artifact": "candidates:255",
      "timestamp": "2026-10-16T12:23:58"
    }
  ],
  "verdict": "UNKNOWN",
  "summary": "6 evidence pieces collected. File is a clean ELF binary."
}

---

## Evidence Sources

| Source | Type | Description |
|--------|------|-------------|
| Static tools | Deterministic | 21 tools in nexus_re_v3.py |
| Agent synthesis | Derived | Combining static evidence |
| RAG grounding | External | NVD/CVE, MITRE ATT&CK, packers |
| Session history | Temporal | Previous analyses (planned) |

---

## RAG Grounding

The RAG service grounds agent claims in authoritative knowledge. Every RAG result cites the source.

Sources:

| Source | Entries | Examples |
|--------|:-------:|----------|
| NVD/CVE | 3 | Log4Shell, Spring4Shell, EternalBlue |
| MITRE ATT&CK | 5 | T1055, T1056, T1486, T1071, T1496 |
| Packer signatures | 2 | UPX, Themida |
| RE tool docs | 2 | Ghidra headless, Frida hooks |

Example RAG query:

Query: ransomware bitcoin

Result:
[MITRE-T1486] Data Encrypted for Impact (Ransomware)
  Severity: CRITICAL
  Score: 0.302

---

## Verdict Determination

The final verdict is determined by aggregating evidence from all agents:

| Condition | Verdict |
|-----------|---------|
| YARA matches ransomware | MALICIOUS |
| Suspicious APIs = CRITICAL | MALICIOUS |
| YARA matches 2+ rules | SUSPICIOUS |
| All tools return clean | UNKNOWN |
| Insufficient evidence | UNKNOWN |

The verdict is always accompanied by the evidence that produced it.

---

## Limitations

Every evidence item carries limitations. Common limitations:

| Limitation | Meaning |
|------------|---------|
| packed_binary | The binary is packed; deep analysis may be inaccurate |
| no_source_code | Source code is not available; results are approximate |
| heuristic_match | Based on patterns, not guaranteed |
| partial_parse | Only part of the file was parsed |
| unknown_format | File format is not recognized |

Limitations are surfaced to the user alongside evidence.

---

## Example: Full Evidence for a Malware Sample

Input: suspicious.exe

Evidence:

1. detect_file_type_hex
   Result: PE (Windows)
   Confidence: HIGH
   Artifact: magic:4d5a

2. calculate_entropy
   Result: 7.82 - HIGH (packed)
   Confidence: HIGH
   Artifact: size:12536

3. detect_packer
   Result: PACKED: YES
   Detected: UPX, VMProtect
   Confidence: HIGH
   Artifact: signatures:upx0,vmp0

4. extract_iocs
   Result: 2 URLs, 1 IP
   Confidence: HIGH
   Artifact: urls:2,ips:1

5. scan_suspicious_apis
   Result: THREAT LEVEL: CRITICAL
   [!] CreateRemoteThread
   [!] VirtualAllocEx
   Confidence: HIGH
   Artifact: apis:2

6. yara_scan
   Result: MALICIOUS (3 rules)
   Confidence: HIGH
   Artifact: rules_matched:3

Verdict: MALICIOUS

Reason: Evidence from 3 HIGH-confidence tools (YARA, APIs, packer) confirms malicious intent.

---

## Traceability

Every claim in a NEXUS-RE report can be traced:

1. Claim: "This file is ransomware."
2. Evidence: YARA matched Ransomware rule.
3. Tool: yara_scan.
4. Artifact: matched string "your files have been encrypted".
5. Confidence: HIGH.

No step in this chain is a black box.

---

## Storing Evidence

Evidence Ledgers are stored in:

- Session memory (in-memory during analysis)
- JSON export (optional, for archival)
- Markdown export (optional, for reports)

The default storage location is:

~/.nexus-re/sessions/SESSION_ID/evidence.json

---

## Ethical Notes

NEXUS-RE never executes binaries automatically. All evidence is derived from static analysis unless the user explicitly enables dynamic analysis.

For malware analysis, always run in an isolated sandbox. For responsible disclosure, follow a 90-day policy.

---

## References

- REA Evidence Contracts: https://github.com/morluto/rea
- NIST SP 800-218 -- Secure Software Development Framework
- Model Context Protocol: https://modelcontextprotocol.io
- MITRE ATT&CK: https://attack.mitre.org
- NVD/CVE: https://nvd.nist.gov