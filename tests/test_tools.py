"""
NEXUS-RE Test Suite - Core Tools
Tests all 21 tools in nexus_re_v3.py
"""

import importlib.util
import unittest
import os
import sys


def load_toolkit():
    spec = importlib.util.spec_from_file_location("nexus_re_v3", "nexus_re_v3.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


toolkit = load_toolkit()


class TestBasicTools(unittest.TestCase):
    """Test basic tools (text input)."""

    def test_hex_dump(self):
        result = toolkit.hex_dump("NEXUS")
        self.assertIn("Size: 5 bytes", result)
        self.assertIn("4e45585553", result)

    def test_hex_dump_empty(self):
        result = toolkit.hex_dump("")
        self.assertIn("Size: 0 bytes", result)

    def test_extract_strings(self):
        result = toolkit.extract_strings("Hello NEXUS-RE testing")
        self.assertIn("Hello", result)
        self.assertIn("NEXUS-RE", result)

    def test_calculate_hash(self):
        result = toolkit.calculate_hash("NEXUS")
        self.assertIn("SHA256:", result)
        self.assertIn("MD5:", result)
        self.assertIn("52b797a276d825aaa28f449f1d35682bd4d271f6455be84e3869", result)

    def test_calculate_entropy_low(self):
        result = toolkit.calculate_entropy("AAAAAAAA")
        self.assertIn("Entropy: 0.0000", result)
        self.assertIn("LOW", result)

    def test_calculate_entropy_medium(self):
        result = toolkit.calculate_entropy("NEXUS-RE")
        self.assertIn("Entropy:", result)

    def test_file_info(self):
        result = toolkit.file_info("test.exe")
        self.assertIn("test.exe", result)
        self.assertIn("NEXUS-RE", result)


class TestBinaryTools(unittest.TestCase):
    """Test binary tools (hex input)."""

    def test_detect_file_type_elf(self):
        result = toolkit.detect_file_type_hex("7f454c46")
        self.assertIn("ELF", result)

    def test_detect_file_type_png(self):
        result = toolkit.detect_file_type_hex("89504e47")
        self.assertIn("PNG", result)

    def test_detect_file_type_invalid(self):
        result = toolkit.detect_file_type_hex("zzzz")
        self.assertIn("Invalid", result)

    def test_parse_elf_header(self):
        elf_hex = "7f454c4602010100000000000000000002003e00010000000010400000000000"
        result = toolkit.parse_elf_header(elf_hex)
        self.assertIn("64-bit", result)
        self.assertIn("x86-64", result)

    def test_extract_iocs_url(self):
        hex_data = "https://malicious.example.com/payload".encode().hex()
        result = toolkit.extract_iocs(hex_data)
        self.assertIn("malicious.example.com", result)

    def test_extract_iocs_ip(self):
        hex_data = "Server IP: 192.168.1.1".encode().hex()
        result = toolkit.extract_iocs(hex_data)
        self.assertIn("192.168.1.1", result)

    def test_xor_bruteforce_v2(self):
        original = b"This is a secret message from NEXUS-RE"
        key = 0x42
        encrypted = bytes(b ^ key for b in original).hex()
        result = toolkit.xor_bruteforce_v2(encrypted)
        self.assertIn("0x42", result)

    def test_scan_suspicious_apis(self):
        hex_data = "CreateRemoteThread VirtualAllocEx".encode().hex()
        result = toolkit.scan_suspicious_apis(hex_data)
        self.assertIn("CRITICAL", result)

    def test_scan_suspicious_apis_clean(self):
        hex_data = "Hello World".encode().hex()
        result = toolkit.scan_suspicious_apis(hex_data)
        self.assertIn("No suspicious", result)

    def test_detect_packer_upx(self):
        hex_data = "UPX0 UPX1".encode().hex()
        result = toolkit.detect_packer(hex_data)
        self.assertIn("PACKED: YES", result)
        self.assertIn("UPX", result)

    def test_detect_packer_clean(self):
        hex_data = "Normal data here".encode().hex()
        result = toolkit.detect_packer(hex_data)
        self.assertIn("PACKED: NO", result)

    def test_yara_ransomware(self):
        hex_data = "your files have been encrypted bitcoin".encode().hex()
        result = toolkit.yara_scan(hex_data)
        self.assertIn("MALICIOUS", result)
        self.assertIn("Ransomware", result)

    def test_yara_clean(self):
        hex_data = "Just a normal file".encode().hex()
        result = toolkit.yara_scan(hex_data)
        self.assertIn("Clean", result)


class TestAdvancedTools(unittest.TestCase):
    """Test advanced tools."""

    def test_version_diff_identical(self):
        hex1 = "4e45585553"
        hex2 = "4e45585553"
        result = toolkit.version_diff(hex1, hex2)
        self.assertIn("IDENTICAL", result)

    def test_version_diff_different(self):
        hex1 = "4e45585553"
        hex2 = "4e45585853"
        result = toolkit.version_diff(hex1, hex2)
        self.assertIn("Changed bytes", result)

    def test_section_analyzer(self):
        hex_data = ("AB" * 128)
        result = toolkit.section_analyzer(hex_data)
        self.assertIn("Section Analyzer", result)

    def test_base64_detector(self):
        import base64
        encoded = base64.b64encode(b"Hello NEXUS-RE").decode()
        hex_data = encoded.encode().hex()
        result = toolkit.base64_detector(hex_data)
        self.assertIn("Base64", result)

    def test_string_similarity_identical(self):
        result = toolkit.string_similarity("NEXUS-RE", "NEXUS-RE")
        self.assertIn("IDENTICAL", result)

    def test_string_similarity_different(self):
        result = toolkit.string_similarity("AAAAAAAA", "ZZZZZZZZ")
        self.assertIn("DIFFERENT", result)


class TestComposite(unittest.TestCase):
    """Test composite tools."""

    def test_full_analysis(self):
        elf_hex = "7f454c4602010100000000000000000002003e00"
        result = toolkit.full_analysis(elf_hex)
        self.assertIn("NEXUS-RE FULL ANALYSIS REPORT", result)
        self.assertIn("FILE TYPE", result)
        self.assertIn("ENTROPY", result)
        self.assertIn("YARA", result)


if __name__ == "__main__":
    print("=" * 65)
    print("  NEXUS-RE Test Suite")
    print("=" * 65)
    print()
    unittest.main(verbosity=2)