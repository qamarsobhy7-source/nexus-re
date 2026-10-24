"""
NEXUS-RE Edge Cases Test Suite
Tests invalid inputs, empty data, and boundary conditions.
"""

import importlib.util
import unittest
import os

DOCS = "/storage/emulated/0/Documents/"

def load_toolkit():
    for p in [DOCS + "nexus_re_v3.py", "/storage/emulated/0/nexus_re_v3.py"]:
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location("nexus_re_v3", p)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
    return None

toolkit = load_toolkit()


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
        r = toolkit.parse_pe_header("7f454c460000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        self.assertIn("Not a PE", r)

    def test_plain_text_as_hex(self):
        r = toolkit.detect_file_type_hex("hello world")
        self.assertIn("Invalid", r)

    def test_large_input_entropy(self):
        r = toolkit.calculate_entropy("A" * 1000000)
        self.assertIn("Entropy", r)

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
