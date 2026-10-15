from mcp.server import MCPServer
import hashlib
import re

mcp = MCPServer("nexus-re")

@mcp.tool()
def hex_dump(text: str) -> str:
    """Convert text to hex dump."""
    data = text.encode('utf-8')
    return f"Size: {len(data)} bytes\nHex: {data.hex()}"

@mcp.tool()
def extract_strings(text: str) -> str:
    """Extract readable strings from binary data."""
    binary_data = b'\x00\x01NEXUS\x00\x02RE\x00\x03Hello World\x00\x04\x05'
    strings = re.findall(rb'[ -~]{4,}', binary_data)
    result = [s.decode('utf-8') for s in strings]
    return "Found strings:\n" + "\n".join(f"  - {s}" for s in result)

@mcp.tool()
def calculate_hash(text: str) -> str:
    """Calculate SHA256 and MD5 hashes."""
    data = text.encode('utf-8')
    return f"SHA256: {hashlib.sha256(data).hexdigest()}\nMD5: {hashlib.md5(data).hexdigest()}"

@mcp.tool()
def file_info(filename: str) -> str:
    """Get basic file information."""
    return f"Filename: {filename}\nAnalyzer: NEXUS-RE v0.1\nStatus: Ready"


@mcp.tool()
def calculate_entropy(text: str) -> str:
    """Calculate Shannon entropy - detects if binary is packed/encrypted."""
    import math
    data = text.encode('utf-8')
    if not data:
        return "Empty data"
    # Count frequency of each byte
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    # Calculate Shannon entropy
    entropy = 0
    for count in freq.values():
        p = count / len(data)
        entropy -= p * math.log2(p)
    # Interpretation
    if entropy > 7.0:
        verdict = "HIGH - Likely packed or encrypted"
    elif entropy > 5.0:
        verdict = "MEDIUM - Possibly compressed"
    else:
        verdict = "LOW - Normal data"
    return f"Entropy: {entropy:.4f}\nVerdict: {verdict}"


@mcp.tool()
def detect_file_type(text: str) -> str:
    """Detect file type from magic number - core RE technique."""
    data = text.encode('utf-8')
    if len(data) < 4:
        return "File too small"
    
    magic = data[:4].hex()
    magic_bytes = data[:4]
    
    signatures = {
        b'\x7fELF': 'ELF Executable (Linux)',
        b'MZ\x90\x00': 'PE Executable (Windows)',
        b'MZ\x90': 'PE Executable (Windows)',
        b'\x89PNG': 'PNG Image',
        b'\xff\xd8\xff\xe0': 'JPEG Image',
        b'PK\x03\x04': 'ZIP Archive',
        b'\x1f\x8b\x08': 'GZIP Archive',
        b'%PDF': 'PDF Document',
        b'\xca\xfe\xba\xbe': 'Java Class / Mach-O',
        b'\x7fELF': 'ELF Executable',
    }
    
    for sig, name in signatures.items():
        if data.startswith(sig):
            return f"Magic: {magic}\nType: {name}\nConfidence: HIGH"
    
    return f"Magic: {magic}\nType: Unknown\nConfidence: LOW"


@mcp.tool()
def detect_file_type_hex(hex_string: str) -> str:
    """Detect file type from hex string - proper RE technique."""
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 4:
        return "File too small"
    
    magic = data[:4].hex()
    
    signatures = {
        b'\x7fELF': 'ELF Executable (Linux)',
        b'MZ\x90\x00': 'PE Executable (Windows)',
        b'\x89PNG': 'PNG Image',
        b'\xff\xd8\xff': 'JPEG Image',
        b'PK\x03\x04': 'ZIP Archive',
        b'\x1f\x8b\x08': 'GZIP Archive',
        b'%PDF': 'PDF Document',
    }
    
    for sig, name in signatures.items():
        if data.startswith(sig):
            return f"Magic: {magic}\nType: {name}\nConfidence: HIGH"
    
    return f"Magic: {magic}\nType: Unknown\nConfidence: LOW"


@mcp.tool()
def parse_elf_header(hex_string: str) -> str:
    """Parse ELF header - extracts architecture, entry point, and type."""
    import struct
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 20:
        return "ELF header too small (need at least 20 bytes)"
    
    if data[:4] != b'\x7fELF':
        return "Not an ELF file"
    
    # ELF class (32 or 64 bit)
    ei_class = data[4]
    bits = "64-bit" if ei_class == 2 else "32-bit" if ei_class == 1 else "Unknown"
    
    # Endianness
    ei_data = data[5]
    endian = "Little-endian" if ei_data == 1 else "Big-endian" if ei_data == 2 else "Unknown"
    fmt = '<' if ei_data == 1 else '>'
    
    # File type
    e_type = struct.unpack(fmt + 'H', data[16:18])[0]
    types = {1: "Relocatable", 2: "Executable", 3: "Shared Object", 4: "Core Dump"}
    file_type = types.get(e_type, f"Unknown ({e_type})")
    
    # Machine (architecture)
    e_machine = struct.unpack(fmt + 'H', data[18:20])[0]
    machines = {0x3e: "x86-64", 0x03: "x86", 0x28: "ARM", 0xb7: "AArch64"}
    arch = machines.get(e_machine, f"Unknown (0x{e_machine:x})")
    
    result = []
    result.append("ELF Header Analysis")
    result.append("=" * 40)
    result.append(f"Format:       ELF")
    result.append(f"Class:        {bits}")
    result.append(f"Endianness:   {endian}")
    result.append(f"Type:         {file_type}")
    result.append(f"Architecture: {arch}")
    
    # Entry point (only if 64-bit)
    if ei_class == 2 and len(data) >= 32:
        e_entry = struct.unpack(fmt + 'Q', data[24:32])[0]
        result.append(f"Entry Point:  0x{e_entry:x}")
    
    return "\n".join(result)


@mcp.tool()
def parse_pe_header(hex_string: str) -> str:
    """Parse PE header - Windows executable analysis."""
    import struct
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 64:
        return "PE header too small"
    
    # Check DOS header
    if data[:2] != b'MZ':
        return "Not a PE file (missing MZ signature)"
    
    # Get PE offset from DOS header (at offset 0x3C)
    pe_offset = struct.unpack('<I', data[0x3C:0x40])[0]
    
    if pe_offset + 24 > len(data):
        return f"PE offset 0x{pe_offset:x} beyond data"
    
    # Check PE signature
    if data[pe_offset:pe_offset+4] != b'PE\x00\x00':
        return "Invalid PE signature"
    
    # Parse COFF header
    coff = data[pe_offset+4:pe_offset+24]
    machine = struct.unpack('<H', coff[0:2])[0]
    num_sections = struct.unpack('<H', coff[2:4])[0]
    timestamp = struct.unpack('<I', coff[4:8])[0]
    characteristics = struct.unpack('<H', coff[18:20])[0]
    
    machines = {
        0x014c: "x86 (32-bit)",
        0x8664: "x86-64 (64-bit)",
        0x01c0: "ARM",
        0xaa64: "ARM64",
    }
    arch = machines.get(machine, f"Unknown (0x{machine:x})")
    
    # Characteristics flags
    flags = []
    if characteristics & 0x0002: flags.append("Executable")
    if characteristics & 0x2000: flags.append("DLL")
    if characteristics & 0x0020: flags.append("Large Address Aware")
    
    result = []
    result.append("PE Header Analysis")
    result.append("=" * 40)
    result.append(f"Format:       PE (Portable Executable)")
    result.append(f"Architecture: {arch}")
    result.append(f"Sections:     {num_sections}")
    result.append(f"Timestamp:    {timestamp}")
    result.append(f"PE Offset:    0x{pe_offset:x}")
    result.append(f"Flags:        {', '.join(flags) if flags else 'None'}")
    
    return "\n".join(result)


@mcp.tool()
def full_analysis(hex_string: str) -> str:
    """Run complete analysis on a binary - combines all tools."""
    import hashlib, struct, re, math
    
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Error: Invalid hex string"
    
    report = []
    report.append("=" * 60)
    report.append("NEXUS-RE FULL BINARY ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")
    
    # 1. Basic Info
    report.append("[1] BASIC INFORMATION")
    report.append("-" * 40)
    report.append(f"Size:  {len(data)} bytes")
    report.append(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    report.append(f"MD5:    {hashlib.md5(data).hexdigest()}")
    report.append("")
    
    # 2. File Type
    report.append("[2] FILE TYPE DETECTION")
    report.append("-" * 40)
    magic = data[:4]
    if magic == b'\x7fELF':
        report.append("Type: ELF (Linux Executable)")
    elif data[:2] == b'MZ':
        report.append("Type: PE (Windows Executable)")
    elif magic == b'\x89PNG':
        report.append("Type: PNG Image")
    elif magic == b'PK\x03\x04':
        report.append("Type: ZIP Archive")
    else:
        report.append(f"Type: Unknown (magic: {magic.hex()})")
    report.append("")
    
    # 3. Entropy
    report.append("[3] ENTROPY ANALYSIS")
    report.append("-" * 40)
    if data:
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        entropy = 0
        for count in freq.values():
            p = count / len(data)
            entropy -= p * math.log2(p)
        report.append(f"Entropy: {entropy:.4f}")
        if entropy > 7.0:
            report.append("Verdict: HIGH - Likely packed/encrypted")
        elif entropy > 5.0:
            report.append("Verdict: MEDIUM - Possibly compressed")
        else:
            report.append("Verdict: LOW - Normal data")
    report.append("")
    
    # 4. Strings
    report.append("[4] EXTRACTED STRINGS")
    report.append("-" * 40)
    strings = re.findall(rb'[ -~]{4,}', data)
    if strings:
        for s in strings[:10]:
            report.append(f"  - {s.decode('utf-8', errors='ignore')}")
    else:
        report.append("  (no strings found)")
    report.append("")
    
    # 5. Security Flags
    report.append("[5] SECURITY ASSESSMENT")
    report.append("-" * 40)
    warnings = []
    if data[:2] == b'MZ':
        warnings.append("PE file - scan with antivirus recommended")
    if entropy > 7.0:
        warnings.append("HIGH entropy - possible obfuscation/packing")
    if b'password' in data.lower():
        warnings.append("Contains 'password' string - check for credentials")
    if b'http://' in data.lower() or b'https://' in data.lower():
        warnings.append("Contains URLs - check for network activity")
    
    if warnings:
        for w in warnings:
            report.append(f"  [!] {w}")
    else:
        report.append("  [OK] No obvious security concerns")
    report.append("")
    
    report.append("=" * 60)
    report.append("END OF REPORT")
    report.append("=" * 60)
    
    return "\n".join(report)


@mcp.tool()
def extract_iocs(hex_string: str) -> str:
    """Extract Indicators of Compromise (IOCs) from binary data."""
    import re
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    text = data.decode('utf-8', errors='ignore')
    
    iocs = {}
    
    # URLs
    urls = re.findall(r'https?://[^\s"\'<>]+', text)
    if urls:
        iocs['URLs'] = list(set(urls))
    
    # IP Addresses
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    valid_ips = [ip for ip in ips if all(0 <= int(o) <= 255 for o in ip.split('.'))]
    if valid_ips:
        iocs['IP Addresses'] = list(set(valid_ips))
    
    # Email Addresses
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if emails:
        iocs['Emails'] = list(set(emails))
    
    # Windows File Paths
    paths = re.findall(r'[A-Z]:\\[^\s"<>|*?]+', text)
    if paths:
        iocs['File Paths'] = list(set(paths))
    
    # Registry Keys
    registry = re.findall(r'HKEY_[A-Z_]+\\[^\s"<>]+', text)
    if registry:
        iocs['Registry Keys'] = list(set(registry))
    
    # Base64 Strings (long ones)
    base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
    base64_strings = re.findall(base64_pattern, text)
    if base64_strings:
        iocs['Base64 Candidates'] = list(set(base64_strings))[:5]
    
    # Build report
    result = []
    result.append("=" * 60)
    result.append("IOC EXTRACTION REPORT")
    result.append("=" * 60)
    
    if not iocs:
        result.append("No IOCs found in data.")
    else:
        total = sum(len(v) for v in iocs.values())
        result.append(f"Total IOCs found: {total}")
        result.append("")
        for category, values in iocs.items():
            result.append(f"[{category}] ({len(values)})")
            for v in values[:10]:
                result.append(f"  - {v}")
            result.append("")
    
    return "\n".join(result)


@mcp.tool()
def xor_bruteforce(hex_string: str) -> str:
    """Brute-force single-byte XOR to find hidden strings - classic malware analysis technique."""
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 4:
        return "Data too small"
    
    # Score function - check for printable ASCII
    def score(decoded):
        printable = sum(1 for b in decoded if 32 <= b < 127)
        return printable / len(decoded) if decoded else 0
    
    results = []
    for key in range(1, 256):
        decoded = bytes(b ^ key for b in data)
        s = score(decoded)
        if s > 0.85:  # At least 85% printable
            try:
                text = decoded.decode('ascii', errors='ignore')
                results.append((s, key, text))
            except:
                pass
    
    # Sort by score
    results.sort(reverse=True)
    
    report = []
    report.append("=" * 60)
    report.append("XOR BRUTE-FORCE ANALYSIS")
    report.append("=" * 60)
    report.append(f"Input size: {len(data)} bytes")
    report.append(f"Candidates found: {len(results)}")
    report.append("")
    
    if not results:
        report.append("No readable XOR decodings found.")
        report.append("Data may use multi-byte XOR or different obfuscation.")
    else:
        report.append("Top 5 candidate keys:")
        report.append("")
        for i, (s, key, text) in enumerate(results[:5], 1):
            report.append(f"[{i}] Key: 0x{key:02x} ({key}) | Score: {s:.2%}")
            report.append(f"    Decoded: {text[:60]}")
            report.append("")
    
    return "\n".join(report)

# Better XOR scoring using English character frequency
import re as _re

def _better_score(data):
    """Score based on English character frequency."""
    if not data:
        return 0
    # English letter frequency (approximate)
    freq = {
        'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0,
        'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,
        'l': 4.0, 'c': 2.8, 'u': 2.8, 'm': 2.4, 'w': 2.4,
        'f': 2.2, 'g': 2.0, 'y': 2.0, 'p': 1.9, 'b': 1.5,
        'v': 1.0, 'k': 0.8, 'j': 0.15, 'x': 0.15, 'q': 0.10,
        'z': 0.07, ' ': 15.0
    }
    text = data.decode('ascii', errors='ignore').lower()
    if len(text) == 0:
        return 0
    score = 0
    total_chars = 0
    for ch in text:
        if ch in freq:
            score += freq[ch]
            total_chars += 1
        elif ch.isalnum():
            score += 1
            total_chars += 1
        else:
            total_chars += 1
    return score / max(total_chars, 1)


def _xor_bruteforce_v2(data):
    results = []
    for key in range(1, 256):
        decoded = bytes(b ^ key for b in data)
        s = _better_score(decoded)
        # Bonus: require it to have spaces (real text has spaces)
        text = decoded.decode('ascii', errors='ignore')
        space_bonus = 5 if ' ' in text else 0
        results.append((s + space_bonus, key, text))
    results.sort(reverse=True)
    return results[:5]

# Override the tool with the improved version
@mcp.tool()
def xor_bruteforce_v2(hex_string: str) -> str:
    """XOR brute-force v2 - uses English frequency scoring for accuracy."""
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 4:
        return "Data too small"
    
    top5 = _xor_bruteforce_v2(data)
    
    report = []
    report.append("=" * 60)
    report.append("XOR BRUTE-FORCE v2 (Frequency-Based)")
    report.append("=" * 60)
    report.append(f"Input size: {len(data)} bytes")
    report.append("")
    report.append("Top 5 candidates:")
    report.append("")
    for i, (s, key, text) in enumerate(top5, 1):
        report.append(f"[{i}] Key: 0x{key:02x} ({key}) | Score: {s:.2f}")
        report.append(f"    Decoded: {text[:60]}")
        report.append("")
    return "\n".join(report)


@mcp.tool()
def scan_suspicious_apis(hex_string: str) -> str:
    """Scan for suspicious Windows APIs used by malware - real threat detection."""
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    text = data.decode('utf-8', errors='ignore')
    
    # Suspicious APIs categorized by threat level
    apis = {
        'CRITICAL': {
            'CreateRemoteThread': 'Process injection - HIGH RISK',
            'VirtualAllocEx': 'Remote memory allocation',
            'WriteProcessMemory': 'Writing to another process',
            'SetWindowsHookEx': 'Keyboard/mouse hooking (keylogger)',
            'GetAsyncKeyState': 'Keylogging',
            'NtUnmapViewOfSection': 'Process hollowing',
            'QueueUserAPC': 'APC injection',
        },
        'HIGH': {
            'VirtualAlloc': 'Memory allocation (shellcode)',
            'LoadLibrary': 'Dynamic DLL loading',
            'GetProcAddress': 'Dynamic API resolution',
            'CreateProcess': 'Process creation',
            'ShellExecute': 'Program execution',
            'WinExec': 'Program execution',
            'URLDownloadToFile': 'File download from internet',
        },
        'MEDIUM': {
            'RegOpenKey': 'Registry access',
            'RegSetValue': 'Registry modification',
            'CreateFile': 'File operations',
            'WriteFile': 'File writing',
            'InternetOpen': 'Network access',
            'HttpSendRequest': 'HTTP communication',
            'socket': 'Network socket',
        },
    }
    
    found = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': []}
    
    for level, api_dict in apis.items():
        for api, desc in api_dict.items():
            if api in text:
                found[level].append(f"{api} — {desc}")
    
    # Build report
    report = []
    report.append("=" * 60)
    report.append("SUSPICIOUS API SCAN REPORT")
    report.append("=" * 60)
    
    total = sum(len(v) for v in found.values())
    
    if total == 0:
        report.append("No suspicious APIs detected.")
        report.append("File appears clean based on API scan.")
    else:
        report.append(f"Total suspicious APIs: {total}")
        report.append("")
        
        # Overall threat level
        if found['CRITICAL']:
            report.append("THREAT LEVEL: CRITICAL")
            report.append("This binary likely contains malicious code!")
        elif found['HIGH']:
            report.append("THREAT LEVEL: HIGH")
            report.append("This binary contains suspicious functionality.")
        else:
            report.append("THREAT LEVEL: MEDIUM")
            report.append("Some APIs require attention.")
        
        report.append("")
        
        for level in ['CRITICAL', 'HIGH', 'MEDIUM']:
            if found[level]:
                report.append(f"[{level}] ({len(found[level])} found)")
                for item in found[level]:
                    report.append(f"  [!] {item}")
                report.append("")
    
    return "\n".join(report)


@mcp.tool()
def detect_packer(hex_string: str) -> str:
    """Detect if binary is packed - analyzes entropy per section."""
    import math
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    if len(data) < 64:
        return "Data too small for packer analysis"
    
    def entropy(block):
        if not block:
            return 0
        freq = {}
        for b in block:
            freq[b] = freq.get(b, 0) + 1
        e = 0
        for c in freq.values():
            p = c / len(block)
            e -= p * math.log2(p)
        return e
    
    # Split into 4 sections
    n = len(data)
    chunk = n // 4
    sections = []
    for i in range(4):
        start = i * chunk
        end = start + chunk if i < 3 else n
        block = data[start:end]
        sections.append(entropy(block))
    
    overall = entropy(data)
    
    # Known packer signatures in the binary
    packers = {
        b'UPX0': 'UPX',
        b'UPX1': 'UPX',
        b'.aspack': 'ASPack',
        b'.adata': 'ASPack',
        b'PECompact': 'PECompact',
        b'Themida': 'Themida',
        b'.vmp0': 'VMProtect',
        b'.vmp1': 'VMProtect',
        b'MPRESS1': 'MPRESS',
        b'.petite': 'Petite',
    }
    
    detected = []
    for sig, name in packers.items():
        if sig in data:
            if name not in detected:
                detected.append(name)
    
    # Build report
    report = []
    report.append("=" * 60)
    report.append("PACKER DETECTION REPORT")
    report.append("=" * 60)
    report.append(f"File size: {n} bytes")
    report.append("")
    
    report.append("[SECTION ENTROPY]")
    report.append("-" * 40)
    for i, e in enumerate(sections, 1):
        bar = "█" * int(e) + "░" * (8 - int(e))
        status = "HIGH" if e > 7.0 else "MED" if e > 5.0 else "LOW"
        report.append(f"  Section {i}: {e:.2f} {bar} [{status}]")
    report.append("")
    
    report.append("[OVERALL]")
    report.append("-" * 40)
    report.append(f"  Overall entropy: {overall:.4f}")
    report.append("")
    
    report.append("[PACKER SIGNATURES]")
    report.append("-" * 40)
    if detected:
        for p in detected:
            report.append(f"  [!] Known packer detected: {p}")
    else:
        report.append("  No known packer signatures found")
    report.append("")
    
    # Verdict
    high_sections = sum(1 for e in sections if e > 7.0)
    
    report.append("[VERDICT]")
    report.append("-" * 40)
    if detected or high_sections >= 2:
        report.append("  PACKED: YES")
        report.append("  This binary is likely packed.")
        report.append("  Recommendation: Unpack before static analysis.")
    elif overall > 6.5:
        report.append("  PACKED: POSSIBLY")
        report.append("  Suspicious entropy pattern detected.")
    else:
        report.append("  PACKED: NO")
        report.append("  Binary appears to be unpacked.")
    
    return "\n".join(report)


@mcp.tool()
def yara_scan(hex_string: str) -> str:
    """Match binary against built-in YARA-like rules for known malware patterns."""
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        return "Invalid hex string"
    
    text = data.decode('utf-8', errors='ignore')
    
    # Simplified YARA-style rules (real patterns from malware analysis)
    rules = [
        {
            'name': 'Ransomware_Note_Generic',
            'severity': 'CRITICAL',
            'strings': ['your files have been encrypted', 'bitcoin', 'decrypt', 'ransom'],
            'description': 'Generic ransomware note pattern'
        },
        {
            'name': 'Keylogger_Behavior',
            'severity': 'CRITICAL',
            'strings': ['GetAsyncKeyState', 'SetWindowsHookEx', 'keylog'],
            'description': 'Keylogger indicators'
        },
        {
            'name': 'Backdoor_Reverse_Shell',
            'severity': 'CRITICAL',
            'strings': ['/bin/sh', 'cmd.exe /c', 'reverse shell', 'nc -e'],
            'description': 'Reverse shell backdoor'
        },
        {
            'name': 'CryptoMiner_Stratum',
            'severity': 'HIGH',
            'strings': ['stratum+tcp://', 'xmrig', 'minergate', 'monero'],
            'description': 'Cryptocurrency miner'
        },
        {
            'name': 'Persistence_Registry',
            'severity': 'HIGH',
            'strings': ['CurrentVersion\\Run', 'schtasks /create', 'startup folder'],
            'description': 'Persistence mechanism'
        },
        {
            'name': 'Credential_Stealer',
            'severity': 'CRITICAL',
            'strings': ['Login Data', 'Cookies', 'wallet.dat', 'passwords.txt'],
            'description': 'Browser credential theft'
        },
        {
            'name': 'Botnet_C2_Pattern',
            'severity': 'HIGH',
            'strings': ['bot.php', 'gate.php', 'c2 server', 'command and control'],
            'description': 'Botnet command and control'
        },
        {
            'name': 'Antivirus_Evasion',
            'severity': 'HIGH',
            'strings': ['Defender', 'MsMpEng', 'StopDefender', 'DisableRealtimeMonitoring'],
            'description': 'Attempts to disable AV'
        },
        {
            'name': 'USB_Spread',
            'severity': 'MEDIUM',
            'strings': ['autorun.inf', 'USB drive', 'removable'],
            'description': 'USB spreading capability'
        },
        {
            'name': 'Suspicious_Packer',
            'severity': 'MEDIUM',
            'strings': ['UPX0', '.aspack', 'Themida', 'VMProtect'],
            'description': 'Packed executable'
        },
    ]
    
    matched_rules = []
    for rule in rules:
        matches = [s for s in rule['strings'] if s.lower() in text.lower()]
        if matches:
            matched_rules.append({
                'name': rule['name'],
                'severity': rule['severity'],
                'description': rule['description'],
                'matches': matches
            })
    
    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    matched_rules.sort(key=lambda r: severity_order.get(r['severity'], 4))
    
    # Build report
    report = []
    report.append("=" * 60)
    report.append("YARA RULE MATCHER REPORT")
    report.append("=" * 60)
    report.append(f"Total rules loaded: {len(rules)}")
    report.append(f"Rules matched: {len(matched_rules)}")
    report.append("")
    
    if not matched_rules:
        report.append("✓ No YARA rules matched.")
        report.append("File appears clean based on known patterns.")
    else:
        for r in matched_rules:
            report.append(f"[{r['severity']}] {r['name']}")
            report.append(f"  Description: {r['description']}")
            report.append(f"  Matches: {', '.join(r['matches'])}")
            report.append("")
        
        # Overall assessment
        critical = sum(1 for r in matched_rules if r['severity'] == 'CRITICAL')
        high = sum(1 for r in matched_rules if r['severity'] == 'HIGH')
        
        report.append("=" * 60)
        if critical > 0:
            report.append(f"ASSESSMENT: MALICIOUS ({critical} critical matches)")
        elif high > 0:
            report.append(f"ASSESSMENT: SUSPICIOUS ({high} high matches)")
        else:
            report.append("ASSESSMENT: POTENTIALLY UNWANTED")
        report.append("=" * 60)
    
    return "\n".join(report)
