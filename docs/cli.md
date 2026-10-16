# NEXUS-RE CLI Reference

> Version: 3.0.0 | Last Updated: 2026-10-16

This document describes the NEXUS-RE Command-Line Interface, including all 21 tools and the interactive menu.

---

## Quick Start

Run the toolkit:

python nexus_re_v3.py

You will see the interactive menu:

---

## Basic Tools (1-6)

### 1. Hex Dump

Purpose: Convert any text to hexadecimal representation.

Input: Text string

Example:

Choose (0-21): 1
Enter text: NEXUS

Output:

Size: 5 bytes
Hex: 4e45585553

### 2. Extract Strings

Purpose: Extract readable ASCII strings (4 or more characters) from binary data.

Input: Text string

Example:

Choose (0-21): 2
Enter text: Hello NEXUS-RE

Output:

Found strings:
  - Hello NEXUS-RE

### 3. Calculate Hash

Purpose: Compute SHA-256 and MD5 digests.

Input: Text string

Example:

Choose (0-21): 3
Enter text: NEXUS

Output:

SHA256: 52b797a276d825aaa28f449f1d35682bd4d271f6455be84e3869cdd7aed2ca03
MD5:    d053b198d88b5d1bb38f86da8c17fdb6

### 4. Calculate Entropy

Purpose: Compute Shannon entropy to detect packed or encrypted data.

Input: Text string

Example:

Choose (0-21): 4
Enter text: NEXUS-RE

Output:

Entropy: 2.7500
Verdict: LOW (normal)

### 5. Detect File Type (text)

Purpose: Identify file type from magic numbers (text mode).

Input: Text starting with magic bytes

Example:

Choose (0-21): 5
Enter text: MZ test

Output:

Type: PE (Windows)
Confidence: HIGH

### 6. File Info

Purpose: Return metadata about a file.

Input: Filename

Example:

Choose (0-21): 6
Enter text: test.exe

Output:

Filename: test.exe
Analyzer: NEXUS-RE v3.0
Status: Ready

---

## Binary Tools (7-15)

### 7. Detect File Type (hex)

Purpose: Identify file type from hex input.

Input: Hex string

Example:

Choose (0-21): 7
Enter hex string: 7f454c46

Output:

Type: ELF (Linux)
Confidence: HIGH

### 8. Parse ELF Header

Purpose: Parse an ELF binary header.

Input: Hex string (at least 20 bytes)

Example:

Choose (0-21): 8
Enter hex string: 7f454c4602010100000000000000000002003e00010000000010400000000000

Output:

ELF Header Analysis
========================================
Class:        64-bit
Endianness:   Little-endian
Type:         Executable
Architecture: x86-64
Entry Point:  0x401000

### 9. Parse PE Header

Purpose: Parse a PE binary header.

Input: Hex string

Example:

Choose (0-21): 9
Enter hex string: 4d5a0000...

Output:

PE Header Analysis
========================================
Architecture: x86-64
Sections:     5
Flags:        Executable, Large Address Aware

### 10. Extract IOCs

Purpose: Extract Indicators of Compromise (URLs, IPs, emails, registry keys, paths).

Input: Hex string

Example:

Choose (0-21): 10
Enter hex string: [hex of URLs and IPs]

Output:

Total IOCs: 3
URLs (2):
  - http://malicious.example.com/payload
  - http://backup.evil.org/data
IPs (1):
  - 192.168.1.100

### 11. XOR Brute Force (v1)

Purpose: Single-byte XOR brute-force using printable-ASCII scoring.

Input: Hex string

### 12. XOR Brute Force (v2 - frequency)

Purpose: Single-byte XOR brute-force using English character frequency scoring.

Input: Hex string

Example:

Choose (0-21): 12
Enter hex string: 162a2b31622b31622362312721302736622f27313123252762

Output:

XOR Brute Force v2 - Top 3:
  Key 0x42 (score 12.83)
    This is a secret message from NEXUS-RE

### 13. Scan Suspicious APIs

Purpose: Detect 20 or more malware-associated Windows APIs.

Input: Hex string

Example:

Choose (0-21): 13
Enter hex string: [hex of CreateRemoteThread]

Output:

Suspicious API Scan:
THREAT LEVEL: CRITICAL
  [!] CreateRemoteThread
  [!] VirtualAllocEx

### 14. Detect Packer

Purpose: Identify UPX, ASPack, Themida, VMProtect, MPRESS, Petite, PECompact.

Input: Hex string

Example:

Choose (0-21): 14
Enter hex string: 55505830

Output:

PACKED: YES
Detected: UPX
Recommendation: Unpack first

### 15. YARA Scan

Purpose: Match against 8 built-in YARA-style rule sets.

Input: Hex string

Example:

Choose (0-21): 15
Enter hex string: 626974636f696e

Output:

YARA: MALICIOUS (1 rules matched)
  [Ransomware]: bitcoin

---

## Advanced Tools (16-21)

### 16. Full Analysis

Purpose: Run all core tools in one call and produce a complete report.

Input: Hex string

Example:

Choose (0-21): 16
Enter hex string: 7f454c4602010100

Output:

NEXUS-RE FULL ANALYSIS REPORT
========================================
Size: 8 bytes
SHA256: ...
MD5:    ...

[1] FILE TYPE
Type: ELF (Linux)

[2] ENTROPY
Entropy: 3.6641

[3] IOCs
No IOCs found

[4] SUSPICIOUS APIs
No suspicious APIs detected

[5] PACKER
PACKED: NO

[6] YARA
YARA: Clean

### 17. Analyze File

Purpose: Read a file from disk and analyze it.

Input: File path

Example:

Choose (0-21): 17
Enter file path: /samples/suspicious.exe

Output: (same as Full Analysis)

### 18. Version Diff

Purpose: Compare two binaries and report differences.

Input: Two hex strings

Example:

Choose (0-21): 18
Enter hex 1: 4e45585553
Enter hex 2: 4e45585853

Output:

Version Diff Report
========================================
File 1 size: 5 bytes
File 2 size: 5 bytes
Size delta:  +0 bytes
Changed bytes: 1
Similarity:    80.00%

First 10 differences (offset: old -> new):
  0x0003: 0x55 -> 0x58

### 19. Section Analyzer

Purpose: Compute entropy per 1/8 chunk to detect hidden sections.

Input: Hex string (at least 64 bytes)

Example:

Choose (0-21): 19
Enter hex string: [128+ bytes]

Output:

Section Analyzer
========================================
Total size: 128 bytes

Entropy per 1/8 chunk:
  [1] 0x0000: 1.00 #....... [LOW]
  [2] 0x0010: 1.00 #....... [LOW]
  ...

### 20. Base64 Detector

Purpose: Detect and decode Base64-encoded strings.

Input: Hex string

Example:

Choose (0-21): 20
Enter hex string: [hex of SGVsbG8gTkVYVVM=]

Output:

Base64 Detector
========================================
Found 1 candidate(s):

[1] SGVsbG8gTkVYVVM=
    Decoded: Hello NEXUS

### 21. String Similarity

Purpose: Compare two strings using 4 similarity metrics.

Input: Two text strings

Example:

Choose (0-21): 21
Enter text 1: NEXUS-RE
Enter text 2: NEXUS-RE

Output:

String Similarity
========================================
String 1: NEXUS-RE
String 2: NEXUS-RE

Jaccard (char set):   100.00%
Character overlap:    100.00%
Length ratio:         100.00%
Positional match:     100.00%

Overall similarity:   100.00%
Verdict: IDENTICAL

---

## Exit

Choose 0 to exit the toolkit.

Choose (0-21): 0
Goodbye!

---

## Python API Usage

All 21 tools can also be used programmatically:

from nexus_re_v3 import (
    hex_dump, extract_strings, calculate_hash, calculate_entropy,
    file_info, detect_file_type, detect_file_type_hex,
    parse_elf_header, parse_pe_header, extract_iocs,
    xor_bruteforce, xor_bruteforce_v2, scan_suspicious_apis,
    detect_packer, yara_scan, full_analysis, analyze_file,
    version_diff, section_analyzer, base64_detector, string_similarity,
)

# Example
result = calculate_hash("NEXUS")
print(result)

---

## Error Handling

Every tool handles invalid input gracefully:

Choose (0-21): 8
Enter hex string: zzzz

Output:

Invalid hex

---

## Performance

| Tool | Average Time |
|------|-------------:|
| hex_dump | < 1 ms |
| extract_strings | < 5 ms |
| calculate_hash | < 1 ms |
| calculate_entropy | < 2 ms |
| parse_elf_header | < 1 ms |
| parse_pe_header | < 1 ms |
| xor_bruteforce_v2 | < 50 ms |
| full_analysis | < 100 ms |

All tools are deterministic and side-effect-free.

---

## References

- README.md -- Project overview
- docs/architecture.md -- System architecture
- docs/testing.md -- Testing guide
- docs/roadmap.md -- Development roadmap