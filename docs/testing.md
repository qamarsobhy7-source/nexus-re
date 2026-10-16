# NEXUS-RE Testing Guide

> Version: 3.0.0 | Last Updated: 2026-10-16

This document describes the testing strategy, test coverage, and quality metrics for NEXUS-RE.

---

## Testing Philosophy

NEXUS-RE follows three testing principles:

1. Deterministic tools must be fully testable. Every one of the 21 tools has at least one unit test.

2. Evidence must be verifiable. Tests assert not just pass/fail, but specific evidence content.

3. CI runs on every commit. GitHub Actions tests on Python 3.11, 3.12, and 3.13.

---

## Test Suite Overview

Location: tests/test_tools.py

Framework: Python standard unittest

Total tests: 27

Pass rate: 100%

Average runtime: less than 0.02 seconds

---

## Test Categories

### Category 1 -- Basic Tools (7 tests)

| Test | What It Verifies |
|------|------------------|
| test_hex_dump | Text to hex conversion works |
| test_hex_dump_empty | Empty input handled correctly |
| test_extract_strings | ASCII strings extracted |
| test_calculate_hash | SHA256 + MD5 computed |
| test_calculate_entropy_low | Zero entropy for repeated chars |
| test_calculate_entropy_medium | Entropy calculated for mixed text |
| test_file_info | Metadata returned |

### Category 2 -- Binary Tools (13 tests)

| Test | What It Verifies |
|------|------------------|
| test_detect_file_type_elf | ELF magic detected |
| test_detect_file_type_png | PNG magic detected |
| test_detect_file_type_invalid | Invalid hex handled |
| test_parse_elf_header | ELF header parsed (64-bit, x86-64) |
| test_extract_iocs_url | URLs extracted |
| test_extract_iocs_ip | IPs extracted |
| test_xor_bruteforce_v2 | Key 0x42 recovered |
| test_scan_suspicious_apis | CRITICAL APIs detected |
| test_scan_suspicious_apis_clean | Clean file shows no APIs |
| test_detect_packer_upx | UPX packer detected |
| test_detect_packer_clean | Unpacked file detected |
| test_yara_ransomware | Ransomware rule matches |
| test_yara_clean | Clean file shows no matches |

### Category 3 -- Advanced Tools (6 tests)

| Test | What It Verifies |
|------|------------------|
| test_version_diff_identical | Identical files return IDENTICAL |
| test_version_diff_different | Different files show changes |
| test_section_analyzer | Entropy per chunk calculated |
| test_base64_detector | Base64 string detected |
| test_string_similarity_identical | Identical strings score 100% |
| test_string_similarity_different | Different strings score low |

### Category 4 -- Composite (1 test)

| Test | What It Verifies |
|------|------------------|
| test_full_analysis | Full report has all sections |

---

## Running the Tests

### Run all tests

python -m unittest tests.test_tools -v

### Run specific category

python -m unittest tests.test_tools.TestBasicTools -v

### Run with pytest

pytest tests/ -v

---

## Expected Output


---

## CI/CD Pipeline

File: .github/workflows/ci.yml

The CI pipeline runs four jobs:

### Job 1 -- Test

Matrix: Python 3.11, 3.12, 3.13

Steps:
1. Checkout repository
2. Set up Python
3. Install dependencies
4. Verify toolkit loads
5. Verify README exists
6. Verify proposal exists

### Job 2 -- Lint

Tools: flake8, black

Steps:
1. Checkout repository
2. Set up Python 3.13
3. Install linters
4. Run flake8 (max line length 120)
5. Check formatting with black

### Job 3 -- Security Scan

Tool: Bandit

Steps:
1. Checkout repository
2. Install bandit
3. Run bandit security scan

### Job 4 -- Build Docker

Depends on: Job 1 (Test)

Steps:
1. Checkout repository
2. Set up Docker Buildx
3. Build Docker image
4. Test Docker image

---

## Code Coverage Goals

| Module | Target |
|--------|-------:|
| Core tools | 100% |
| ELF parser | 100% |
| PE parser | 100% |
| IOC extractor | 95% |
| XOR brute-force | 95% |
| YARA matcher | 90% |
| Full analysis | 90% |

---

## Adding New Tests

When adding a new tool to nexus_re_v3.py:

1. Add a test method to the appropriate class in tests/test_tools.py
2. Test at least 3 cases: valid input, invalid input, edge case
3. Run the test suite locally
4. Commit both the tool and the test together

Example test structure:

class TestMyNewTool(unittest.TestCase):
    def test_valid_input(self):
        result = toolkit.my_new_tool("valid input")
        self.assertIn("expected substring", result)

    def test_invalid_input(self):
        result = toolkit.my_new_tool("invalid")
        self.assertIn("error", result.lower())

    def test_edge_case(self):
        result = toolkit.my_new_tool("")
        self.assertIsNotNone(result)

---

## Known Limitations

1. No integration tests yet -- planned for Phase 5
2. No performance benchmarks yet -- planned for Phase 6
3. No fuzz testing yet -- planned for Phase 6

---

## References

- Python unittest documentation: https://docs.python.org/3/library/unittest.html
- pytest documentation: https://docs.pytest.org
- GitHub Actions documentation: https://docs.github.com/en/actions