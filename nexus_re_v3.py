"""
NEXUS-RE v3.0 - Complete Reverse Engineering Toolkit
21 Tools + File Analysis + Version Diff
"""
import sys
import hashlib, re, math, struct, os

# ==================== TOOLS ====================

def hex_dump(text):
    data = text.encode('utf-8')
    return f"Size: {len(data)} bytes\nHex: {data.hex()}"

def extract_strings(text):
    data = text.encode('utf-8', errors='ignore')
    strings = re.findall(rb'[ -~]{4,}', data)
    if not strings: return "No strings found"
    out = ["Found strings:"]
    for s in strings: out.append(f"  - {s.decode('utf-8', errors='ignore')}")
    return "\n".join(out)

def calculate_hash(text):
    data = text.encode('utf-8')
    return f"SHA256: {hashlib.sha256(data).hexdigest()}\nMD5: {hashlib.md5(data).hexdigest()}"

def calculate_entropy(text):
    data = text.encode('utf-8')
    if not data: return "Empty"
    freq = {}
    for b in data: freq[b] = freq.get(b, 0) + 1
    e = 0
    for c in freq.values():
        p = c / len(data); e -= p * math.log2(p)
    v = "HIGH (packed/encrypted)" if e > 7.0 else "MEDIUM" if e > 5.0 else "LOW (normal)"
    return f"Entropy: {e:.4f}\nVerdict: {v}"

def file_info(filename):
    return f"Filename: {filename}\nAnalyzer: NEXUS-RE v2.0\nStatus: Ready"

def detect_file_type(text):
    data = text.encode('utf-8', errors='ignore')
    if len(data) < 4: return "File too small"
    sigs = [(b'\x7fELF','ELF (Linux)'),(b'MZ','PE (Windows)'),
            (b'\x89PNG','PNG Image'),(b'PK\x03\x04','ZIP Archive'),
            (b'%PDF','PDF'),(b'\x1f\x8b\x08','GZIP')]
    for sig, name in sigs:
        if data.startswith(sig): return f"Type: {name}\nConfidence: HIGH"
    return f"Type: Unknown\nMagic: {data[:4].hex()}"

def detect_file_type_hex(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    sigs = [(b'\x7fELF','ELF (Linux)'),(b'MZ','PE (Windows)'),
            (b'\x89PNG','PNG Image'),(b'PK\x03\x04','ZIP Archive'),
            (b'%PDF','PDF'),(b'\x1f\x8b\x08','GZIP')]
    for sig, name in sigs:
        if data.startswith(sig): return f"Type: {name}\nConfidence: HIGH"
    return f"Unknown (magic: {data[:4].hex()})"

def parse_elf_header(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    if len(data) < 4: return "ELF header too small"
    if data[:4] != b'\x7fELF': return "Not an ELF file"
    if len(data) < 20: return "ELF header too small"
    ei_class = data[4]
    bits = "64-bit" if ei_class == 2 else "32-bit" if ei_class == 1 else "Unknown"
    ei_data = data[5]
    endian = "Little-endian" if ei_data == 1 else "Big-endian" if ei_data == 2 else "?"
    fmt = '<' if ei_data == 1 else '>'
    e_type = struct.unpack(fmt + 'H', data[16:18])[0]
    types = {1:"Relocatable",2:"Executable",3:"Shared Object",4:"Core Dump"}
    ft = types.get(e_type, f"Unknown ({e_type})")
    e_machine = struct.unpack(fmt + 'H', data[18:20])[0]
    machines = {0x3e:"x86-64",0x03:"x86",0x28:"ARM",0xb7:"AArch64"}
    arch = machines.get(e_machine, f"Unknown (0x{e_machine:x})")
    out = ["ELF Header Analysis", "=" * 40]
    out.append(f"Class:        {bits}")
    out.append(f"Endianness:   {endian}")
    out.append(f"Type:         {ft}")
    out.append(f"Architecture: {arch}")
    if ei_class == 2 and len(data) >= 32:
        e_entry = struct.unpack(fmt + 'Q', data[24:32])[0]
        out.append(f"Entry Point:  0x{e_entry:x}")
    return "\n".join(out)

def parse_pe_header(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    if len(data) < 64: return "PE header too small"
    if data[:2] != b'MZ': return "Not a PE file"
    pe_offset = struct.unpack('<I', data[0x3C:0x40])[0]
    if pe_offset + 24 > len(data): return f"PE offset 0x{pe_offset:x} beyond data"
    if data[pe_offset:pe_offset+4] != b'PE\x00\x00': return "Invalid PE signature"
    coff = data[pe_offset+4:pe_offset+24]
    machine = struct.unpack('<H', coff[0:2])[0]
    sections = struct.unpack('<H', coff[2:4])[0]
    ts = struct.unpack('<I', coff[4:8])[0]
    chars = struct.unpack('<H', coff[18:20])[0]
    machines = {0x014c:"x86",0x8664:"x86-64",0x01c0:"ARM",0xaa64:"ARM64"}
    arch = machines.get(machine, f"Unknown (0x{machine:x})")
    flags = []
    if chars & 0x0002: flags.append("Executable")
    if chars & 0x2000: flags.append("DLL")
    if chars & 0x0020: flags.append("Large Address Aware")
    out = ["PE Header Analysis", "=" * 40]
    out.append(f"Architecture: {arch}")
    out.append(f"Sections:     {sections}")
    out.append(f"Timestamp:    {ts}")
    out.append(f"PE Offset:    0x{pe_offset:x}")
    out.append(f"Flags:        {', '.join(flags) if flags else 'None'}")
    return "\n".join(out)

def extract_iocs(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore')
    urls = list(set(re.findall(r'https?://[^\s"\'<>]+', text)))
    ips = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)))
    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
    reg = list(set(re.findall(r'HKEY_[A-Z_]+\\[^\s"<>]+', text)))
    paths = list(set(re.findall(r'[A-Z]:\\[^\s"<>|*?]+', text)))
    out = [f"Total IOCs: {len(urls)+len(ips)+len(emails)+len(reg)+len(paths)}"]
    if urls: out.append(f"URLs ({len(urls)}):"); [out.append(f"  - {u}") for u in urls[:5]]
    if ips: out.append(f"IPs ({len(ips)}):"); [out.append(f"  - {i}") for i in ips[:5]]
    if emails: out.append(f"Emails ({len(emails)}):"); [out.append(f"  - {e}") for e in emails[:5]]
    if reg: out.append(f"Registry ({len(reg)}):"); [out.append(f"  - {r}") for r in reg[:3]]
    if paths: out.append(f"Paths ({len(paths)}):"); [out.append(f"  - {p}") for p in paths[:3]]
    return "\n".join(out) if len(out) > 1 else "No IOCs found"


def xor_bruteforce(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    if len(data) < 4: return "Data too small"
    def score(decoded):
        printable = sum(1 for b in decoded if 32 <= b < 127)
        return printable / len(decoded) if decoded else 0
    results = []
    for key in range(1, 256):
        dec = bytes(b ^ key for b in data)
        s = score(dec)
        if s > 0.85:
            results.append((s, key, dec.decode('ascii', errors='ignore')))
    results.sort(reverse=True)
    out = ["XOR Brute Force v1 - Top 5 (basic):"]
    for s, k, t in results[:5]:
        out.append(f"  Key 0x{k:02x} (score {s:.2%})")
        out.append(f"    {t[:60]}")
    return "\n".join(out) if len(out) > 1 else "No readable decodings"

def xor_bruteforce_v2(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    freq = {'e':12.7,'t':9.1,'a':8.2,'o':7.5,'i':7.0,'n':6.7,'s':6.3,'h':6.1,
            'r':6.0,'d':4.3,'l':4.0,'c':2.8,'u':2.8,'m':2.4,'w':2.4,' ':15.0}
    results = []
    for key in range(1, 256):
        dec = bytes(b ^ key for b in data)
        text = dec.decode('ascii', errors='ignore').lower()
        if not text: continue
        score = sum(freq.get(c, 0.5) for c in text) / len(text)
        if ' ' in text: score += 5
        results.append((score, key, dec.decode('ascii', errors='ignore')))
    results.sort(reverse=True)
    out = ["XOR Brute Force v2 - Top 3:"]
    for s, k, t in results[:3]:
        out.append(f"  Key 0x{k:02x} (score {s:.1f})")
        out.append(f"    {t[:60]}")
    return "\n".join(out)

def scan_suspicious_apis(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore')
    critical = ['CreateRemoteThread','VirtualAllocEx','WriteProcessMemory',
                'GetAsyncKeyState','SetWindowsHookEx','NtUnmapViewOfSection','QueueUserAPC']
    high = ['VirtualAlloc','LoadLibrary','GetProcAddress','CreateProcess',
            'URLDownloadToFile','ShellExecute','WinExec']
    found_c = [a for a in critical if a in text]
    found_h = [a for a in high if a in text]
    out = ["Suspicious API Scan:"]
    if found_c:
        out.append(f"THREAT LEVEL: CRITICAL")
        [out.append(f"  [!] {a}") for a in found_c]
    if found_h:
        out.append(f"THREAT LEVEL: HIGH")
        [out.append(f"  [!] {a}") for a in found_h]
    if not found_c and not found_h:
        out.append("No suspicious APIs detected")
    return "\n".join(out)

def detect_packer(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    packers = [(b'UPX0','UPX'),(b'UPX1','UPX'),(b'.aspack','ASPack'),
               (b'Themida','Themida'),(b'.vmp0','VMProtect'),(b'MPRESS1','MPRESS'),
               (b'.petite','Petite'),(b'PECompact','PECompact')]
    detected = []
    for sig, name in packers:
        if sig in data and name not in detected: detected.append(name)
    if detected:
        return f"PACKED: YES\nDetected: {', '.join(detected)}\nRecommendation: Unpack first"
    return "PACKED: NO\nBinary appears unpacked"

def yara_scan(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore').lower()
    rules = {
        'Ransomware': ['your files have been encrypted','bitcoin','decrypt','ransom'],
        'Keylogger': ['getasynckeystate','setwindowshookex','keylog'],
        'Credential Stealer': ['login data','cookies','wallet.dat','passwords.txt'],
        'Crypto Miner': ['stratum+tcp://','xmrig','monero','minergate'],
        'Botnet C2': ['bot.php','gate.php','c2 server','command and control'],
        'Antivirus Evasion': ['stopdefender','disablerealtimemonitoring'],
        'Reverse Shell': ['/bin/sh','cmd.exe /c','reverse shell','nc -e'],
        'Persistence': ['currentversion\\run','schtasks /create'],
    }
    matches = []
    for name, sigs in rules.items():
        found = [s for s in sigs if s in text]
        if found: matches.append(f"  [{name}]: {', '.join(found)}")
    if matches:
        return f"YARA: MALICIOUS ({len(matches)} rules matched)\n" + "\n".join(matches)
    return "YARA: Clean (no patterns matched)"

def full_analysis(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    out = ["=" * 55, "NEXUS-RE FULL ANALYSIS REPORT", "=" * 55, ""]
    out.append(f"Size: {len(data)} bytes")
    out.append(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    out.append(f"MD5:    {hashlib.md5(data).hexdigest()}")
    out.append("")
    out.append("[1] FILE TYPE")
    out.append(detect_file_type_hex(hex_string))
    out.append("")
    out.append("[2] ENTROPY")
    out.append(calculate_entropy(data.decode('latin-1', errors='ignore')))
    out.append("")
    out.append("[3] IOCs")
    out.append(extract_iocs(hex_string))
    out.append("")
    out.append("[4] SUSPICIOUS APIs")
    out.append(scan_suspicious_apis(hex_string))
    out.append("")
    out.append("[5] PACKER")
    out.append(detect_packer(hex_string))
    out.append("")
    out.append("[6] YARA")
    out.append(yara_scan(hex_string))
    out.append("")
    out.append("=" * 55)
    return "\n".join(out)

def analyze_file(path):
    try:
        with open(path, 'rb') as f: data = f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    hex_string = data.hex()
    return full_analysis(hex_string)

# ==================== MAIN MENU ====================


def version_diff(hex1, hex2):
    """Compare two binaries and report differences."""
    try:
        d1 = bytes.fromhex(hex1)
        d2 = bytes.fromhex(hex2)
    except:
        return "Invalid hex input"
    out = ["Version Diff Report", "=" * 50]
    out.append(f"File 1 size: {len(d1)} bytes")
    out.append(f"File 2 size: {len(d2)} bytes")
    out.append(f"Size delta:  {len(d2) - len(d1):+d} bytes")
    if d1 == d2:
        out.append("")
        out.append("Result: IDENTICAL")
        return "\n".join(out)
    min_len = min(len(d1), len(d2))
    diff_count = sum(1 for i in range(min_len) if d1[i] != d2[i])
    similarity = 100 * (1 - diff_count / min_len) if min_len else 0
    out.append(f"Changed bytes: {diff_count}")
    out.append(f"Similarity:    {similarity:.2f}%")
    out.append("")
    out.append("First 10 differences (offset: old -> new):")
    shown = 0
    for i in range(min_len):
        if d1[i] != d2[i]:
            out.append(f"  0x{i:04x}: 0x{d1[i]:02x} -> 0x{d2[i]:02x}")
            shown += 1
            if shown >= 10:
                break
    return "\n".join(out)

def section_analyzer(hex_string):
    """Analyze binary sections - entropy per 1/8 chunk."""
    import math
    try:
        data = bytes.fromhex(hex_string)
    except:
        return "Invalid hex"
    if len(data) < 64:
        return "Data too small for section analysis"
    out = ["Section Analyzer", "=" * 50]
    out.append(f"Total size: {len(data)} bytes")
    out.append("")
    out.append("Entropy per 1/8 chunk:")
    chunk_size = len(data) // 8
    for i in range(8):
        start = i * chunk_size
        end = start + chunk_size if i < 7 else len(data)
        chunk = data[start:end]
        if not chunk: continue
        freq = {}
        for b in chunk:
            freq[b] = freq.get(b, 0) + 1
        e = 0
        for c in freq.values():
            p = c / len(chunk)
            e -= p * math.log2(p)
        bar = "#" * int(e) + "." * (8 - int(e))
        verdict = "HIGH" if e > 7 else "MED" if e > 5 else "LOW"
        out.append(f"  [{i+1}] 0x{start:04x}: {e:.2f} {bar} [{verdict}]")
    return "\n".join(out)

def base64_detector(hex_string):
    """Detect and decode Base64-encoded strings in binary data."""
    import re
    try:
        data = bytes.fromhex(hex_string)
    except:
        return "Invalid hex"
    text = data.decode('utf-8', errors='ignore')
    pattern = r'[A-Za-z0-9+/]{16,}={0,2}'
    candidates = re.findall(pattern, text)
    out = ["Base64 Detector", "=" * 50]
    if not candidates:
        out.append("No Base64 candidates found.")
        return "\n".join(out)
    out.append(f"Found {len(candidates)} candidate(s):")
    out.append("")
    import base64
    for i, c in enumerate(candidates[:5], 1):
        out.append(f"[{i}] {c[:60]}{'...' if len(c) > 60 else ''}")
        try:
            decoded = base64.b64decode(c + '=' * (-len(c) % 4))
            decoded_text = decoded.decode('utf-8', errors='ignore')
            printable = sum(1 for ch in decoded_text if 32 <= ord(ch) < 127)
            ratio = printable / len(decoded_text) if decoded_text else 0
            if ratio > 0.8:
                out.append(f"    Decoded: {decoded_text[:60]}")
            else:
                out.append(f"    Decoded: (binary, {len(decoded)} bytes)")
        except:
            out.append(f"    Decode failed")
        out.append("")
    return "\n".join(out)

def string_similarity(text1, text2):
    """Calculate similarity between two strings using multiple metrics."""
    if not text1 or not text2:
        return "Empty input"
    out = ["String Similarity", "=" * 50]
    out.append(f"String 1: {text1[:50]}")
    out.append(f"String 2: {text2[:50]}")
    out.append("")
    s1, s2 = set(text1), set(text2)
    jaccard = len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0
    common = sum(1 for c in set(text1) if c in text2)
    overlap = common / max(len(set(text1)), 1)
    len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
    match = sum(1 for a, b in zip(text1, text2) if a == b)
    pos_match = match / max(len(text1), len(text2))
    out.append(f"Jaccard (char set):   {jaccard:.2%}")
    out.append(f"Character overlap:    {overlap:.2%}")
    out.append(f"Length ratio:         {len_ratio:.2%}")
    out.append(f"Positional match:     {pos_match:.2%}")
    out.append("")
    avg = (jaccard + overlap + len_ratio + pos_match) / 4
    verdict = "IDENTICAL" if avg > 0.95 else "VERY SIMILAR" if avg > 0.7 else "SIMILAR" if avg > 0.4 else "DIFFERENT"
    out.append(f"Overall similarity:   {avg:.2%}")
    out.append(f"Verdict: {verdict}")
    return "\n".join(out)


# ==================== 10 NEW TOOLS ====================

def pe_section_analyzer(hex_string):
    """Analyze PE sections (name, size, permissions)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    if len(data) < 64 or data[:2] != b'MZ': return "Not a PE file"
    out = ["PE Section Analyzer", "=" * 40]
    out.append("Note: Full PE section parsing requires struct offsets.")
    out.append("Basic check: MZ header detected.")
    out.append(f"File size: {len(data)} bytes")
    return "\n".join(out)

def elf_section_analyzer(hex_string):
    """Analyze ELF sections (name, size, type)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    if len(data) < 20 or data[:4] != b'\x7fELF': return "Not an ELF file"
    out = ["ELF Section Analyzer", "=" * 40]
    out.append("Note: Full ELF section parsing requires struct offsets.")
    out.append("Basic check: ELF header detected.")
    out.append(f"File size: {len(data)} bytes")
    return "\n".join(out)

def import_table_parser(hex_string):
    """Parse import table (PE) or dynamic section (ELF)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('latin-1', errors='ignore')
    dlls = re.findall(r'[a-zA-Z0-9_]+\.dll', text, re.IGNORECASE)
    out = ["Import Table Parser", "=" * 40]
    if dlls:
        out.append(f"Found {len(dlls)} DLL imports:")
        for d in set(dlls): out.append(f"  - {d}")
    else:
        out.append("No DLL imports found (may be ELF or packed)")
    return "\n".join(out)

def export_table_parser(hex_string):
    """Parse export table (PE)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    out = ["Export Table Parser", "=" * 40]
    out.append("Note: Requires full PE parsing. Basic check only.")
    out.append(f"Size: {len(data)} bytes")
    return "\n".join(out)

def anti_debug_detector(hex_string):
    """Detect anti-debugging techniques."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('latin-1', errors='ignore').lower()
    apis = ['isdebuggerpresent', 'checkremotedebuggerpresent', 'ntqueryinformationprocess',
            'outputdebugstring', 'ptrace', 'gettickcount']
    found = [api for api in apis if api in text]
    out = ["Anti-Debug Detector", "=" * 40]
    if found:
        out.append(f"THREAT LEVEL: HIGH")
        out.append(f"Found {len(found)} anti-debug APIs:")
        for api in found: out.append(f"  [!] {api}")
    else:
        out.append("No anti-debug APIs detected")
    return "\n".join(out)

def crypto_constant_scanner(hex_string):
    """Detect cryptographic constants (AES, SHA, MD5)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    constants = {
        'AES S-Box': b'\x63\x7c\x77\x7b',
        'SHA-256 Init': b'\x6a\x09\xe6\x67',
        'MD5 Init': b'\x01\x23\x45\x67',
        'CRC32 Table': b'\x00\x00\x00\x00',
    }
    out = ["Crypto Constant Scanner", "=" * 40]
    found = 0
    for name, const in constants.items():
        if const in data:
            out.append(f"  [FOUND] {name} constant detected")
            found += 1
    if found == 0:
        out.append("No known crypto constants found")
    return "\n".join(out)

def string_obfuscation_detector(hex_string):
    """Detect string obfuscation (high entropy short strings)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('latin-1', errors='ignore')
    strings = re.findall(r'[ -~]{8,}', text)
    suspicious = 0
    for s in strings:
        if len(set(s)) > len(s) * 0.8:  # حروف متنوعة جدًا
            suspicious += 1
    out = ["String Obfuscation Detector", "=" * 40]
    out.append(f"Total strings: {len(strings)}")
    out.append(f"Suspicious (high variety): {suspicious}")
    if suspicious > len(strings) * 0.5:
        out.append("WARNING: High string obfuscation detected")
    else:
        out.append("String patterns appear normal")
    return "\n".join(out)

def apk_manifest_parser(hex_string):
    """Parse AndroidManifest.xml from APK (basic)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('latin-1', errors='ignore')
    out = ["APK Manifest Parser", "=" * 40]
    if 'android' in text.lower() or 'manifest' in text.lower():
        out.append("AndroidManifest indicators found")
        perms = re.findall(r'android\.permission\.[A-Z_]+', text)
        if perms:
            out.append(f"Permissions ({len(perms)}):")
            for p in list(set(perms))[:10]: out.append(f"  - {p}")
    else:
        out.append("No AndroidManifest detected")
    return "\n".join(out)

def certificate_extractor(hex_string):
    """Extract digital certificates (basic)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('latin-1', errors='ignore')
    out = ["Certificate Extractor", "=" * 40]
    cert_patterns = ['BEGIN CERTIFICATE', 'BEGIN RSA', 'BEGIN PUBLIC KEY']
    found = [p for p in cert_patterns if p in text]
    if found:
        out.append("Certificates found:")
        for f in found: out.append(f"  - {f}")
    else:
        out.append("No digital certificates detected")
    return "\n".join(out)

def deep_packer_scanner(hex_string):
    """Deeper packer detection (more signatures)."""
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    packers = [(b'UPX', 'UPX'), (b'.aspack', 'ASPack'), (b'MPRESS', 'MPRESS'),
               (b'PECompact', 'PECompact'), (b'Themida', 'Themida'),
               (b'VMProtect', 'VMProtect'), (b'Enigma', 'Enigma'),
               (b'Obsidium', 'Obsidium'), (b'Armadillo', 'Armadillo')]
    found = []
    for sig, name in packers:
        if sig in data and name not in found:
            found.append(name)
    out = ["Deep Packer Scanner", "=" * 40]
    if found:
        out.append("PACKED: YES")
        out.append(f"Detected: {', '.join(found)}")
    else:
        out.append("PACKED: NO")
    return "\n".join(out)


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("NEXUS-RE v3.0 — Reverse Engineering Toolkit")
        print()
        print("Usage:")
        print("  python nexus_re_v3.py            # interactive menu")
        print("  python nexus_re_v3.py --help     # this message")
        print()
        print("Or use as a library:")
        print("  import nexus_re_v3 as t")
        print("  t.hex_dump('hello')")
        return
    print("=" * 55)
    print("  NEXUS-RE v3.0 - Reverse Engineering Toolkit")
    print("  31 Tools | File Analysis | Version Diff")
    print("=" * 55)
    print()
    print("--- BASIC (text input) ---")
    print(" 1. Hex Dump")
    print(" 2. Extract Strings")
    print(" 3. Calculate Hash")
    print(" 4. Calculate Entropy")
    print(" 5. Detect File Type (text)")
    print(" 6. File Info")
    print()
    print("--- BINARY (hex input) ---")
    print(" 7. Detect File Type (hex)")
    print(" 8. Parse ELF Header")
    print(" 9. Parse PE Header")
    print("10. Extract IOCs")
    print("11. XOR Brute Force (v1)")
    print("12. XOR Brute Force (v2 - frequency)")
    print("13. Scan Suspicious APIs")
    print("14. Detect Packer")
    print("15. YARA Scan")
    print()
    print("--- ADVANCED ---")
    print("16. Full Analysis (hex input)")
    print("17. Analyze File (file path)")
    print("18. Version Diff (two hex inputs)")
    print("19. Section Analyzer (hex input)")
    print("20. Base64 Detector (hex input)")
    print("21. String Similarity (two text inputs)")
    print()
    print("--- NEW TOOLS (v3.1) ---")
    print("22. PE Section Analyzer (hex)")
    print("23. ELF Section Analyzer (hex)")
    print("24. Import Table Parser (hex)")
    print("25. Export Table Parser (hex)")
    print("26. Anti-Debug Detector (hex)")
    print("27. Crypto Constant Scanner (hex)")
    print("28. String Obfuscation Detector (hex)")
    print("29. APK Manifest Parser (hex)")
    print("30. Certificate Extractor (hex)")
    print("31. Deep Packer Scanner (hex)")
    print()
    print(" 0. Exit")
    print()
    choice = input("Choose (0-31): ").strip()
    if choice == "0":
        print("Goodbye!")
        return
    print()

    text_tools = {
        "1": hex_dump, "2": extract_strings, "3": calculate_hash,
        "4": calculate_entropy, "5": detect_file_type, "6": file_info,
    }
    hex_tools = {
        "7": detect_file_type_hex, "8": parse_elf_header,
        "9": parse_pe_header, "10": extract_iocs,
        "11": xor_bruteforce, "12": xor_bruteforce_v2,
        "13": scan_suspicious_apis, "14": detect_packer,
        "15": yara_scan, "16": full_analysis,
        "19": section_analyzer, "20": base64_detector,
        "22": pe_section_analyzer, "23": elf_section_analyzer,
        "24": import_table_parser, "25": export_table_parser,
        "26": anti_debug_detector, "27": crypto_constant_scanner,
        "28": string_obfuscation_detector, "29": apk_manifest_parser,
        "30": certificate_extractor, "31": deep_packer_scanner,
    }

    if choice in text_tools:
        text = input("Enter text: ").strip()
        print()
        print("=" * 55)
        print(text_tools[choice](text))
        print("=" * 55)
    elif choice in hex_tools:
        text = input("Enter hex string: ").strip()
        print()
        print("=" * 55)
        print(hex_tools[choice](text))
        print("=" * 55)
    elif choice == "17":
        path = input("Enter file path: ").strip()
        print()
        print(analyze_file(path))
    elif choice == "18":
        hex1 = input("Enter hex 1: ").strip()
        hex2 = input("Enter hex 2: ").strip()
        print()
        print("=" * 55)
        print(version_diff(hex1, hex2))
        print("=" * 55)
    elif choice == "21":
        t1 = input("Enter text 1: ").strip()
        t2 = input("Enter text 2: ").strip()
        print()
        print("=" * 55)
        print(string_similarity(t1, t2))
        print("=" * 55)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()