"""
NEXUS-RE Edge Cases Test Suite
Tests invalid inputs, empty data, and boundary conditions.
"""
import importlib.util
import os
import unittest
import sys

# Use relative path (works in CI and on any device)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TEST_DIR)

# Search for toolkit in multiple locations (relative, not absolute)
def find_toolkit():
    candidates = [
        os.path.join(REPO_ROOT, "nexus_re_v3.py"),
        os.path.join(REPO_ROOT, "src", "tools", "nexus_re_v3.py"),
        os.path.join(REPO_ROOT, "nexus_re_v2.py"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_toolkit():
    path = find_toolkit()
    if not path:
        return None
    spec = importlib.util.spec_from_file_location("nexus_re_v3", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

toolkit = load_toolkit()


@unittest.skipIf(toolkit is None, "Toolkit not found")
class TestEdgeCases(unittest.TestCase):
    """Edge cases: empty, invalid, huge, boundary inputs."""

    def test_hex_dump_empty(self):
        r = toolkit.hex_dump("")
        self.assertIn("0 bytes", r)

    def test_calculate_hash_empty(self):
        r = toolkit.calculate_hash("")
        self.assertIn("SHA256", r)

    def test_calculate_entropy_empty(self):
        r = toolkit.calculate_entropy("")
        self.assertIn("Empty", r)

    def test_invalid_hex_detect_type(self):
        r = toolkit.detect_file_type_hex("zzzz")
        self.assertIn("Invalid", r)

    def test_invalid_hex_parse_elf(self):
        r = toolkit.parse_elf_header("not-hex")
        self.assertIn("Invalid", r)

    def test_invalid_hex_parse_pe(self):
        r = toolkit.parse_pe_header("xyz")
        self.assertIn("Invalid", r)

    def test_too_small_elf(self):
        r = toolkit.parse_elf_header("7f454c46")
        self.assertIn("too small", r)

    def test_too_small_pe(self):
        r = toolkit.parse_pe_header("4d5a")
        self.assertIn("too small", r)

    def test_too_small_xor(self):
        r = toolkit.xor_bruteforce("41")
        self.assertIn("too small", r.lower())

    def test_not_elf(self):
        r = toolkit.parse_elf_header("4d5a0000000000000000")
        self.assertIn("Not an ELF", r)

    def test_not_pe(self):
        r = toolkit.parse_pe_header("7f454c46" + "00" * 80)
        self.assertIn("Not a PE", r)

    def test_plain_text_as_hex(self):
        r = toolkit.detect_file_type_hex("hello world")
        self.assertIn("Invalid", r)

    def test_special_chars(self):
        r = toolkit.hex_dump("!@#$%^&*()")
        self.assertIn("bytes", r)

    def test_yara_clean_file(self):
        r = toolkit.yara_scan("48656c6c6f")
        self.assertIn("Clean", r)

    def test_version_diff_identical(self):
        r = toolkit.version_diff("4e45585553", "4e45585553")
        self.assertIn("IDENTICAL", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
