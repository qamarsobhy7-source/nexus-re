"""
NEXUS-RE v2.0 - Complete Reverse Engineering Toolkit
16 Tools + File Analysis + Report Saving
"""
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
    if len(data) < 20: return "ELF header too small"
    if data[:4] != b'\x7fELF': return "Not an ELF file"
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

def main():
    print("=" * 55)
    print("  NEXUS-RE v2.0 - Reverse Engineering Toolkit")
    print("  16 Tools | File Analysis | Report Saving")
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
    print("11. XOR Brute Force")
    print("12. Scan Suspicious APIs")
    print("13. Detect Packer")
    print("14. YARA Scan")
    print()
    print("--- ADVANCED ---")
    print("15. Full Analysis (hex input)")
    print("16. Analyze File (file path)")
    print()
    print(" 0. Exit")
    print()
    choice = input("Choose (0-16): ").strip()
    if choice == "0":
        print("Goodbye!")
        return
    print()
    text_tools = {"1":hex_dump,"2":extract_strings,"3":calculate_hash,
                  "4":calculate_entropy,"5":detect_file_type,"6":file_info}
    hex_tools = {"7":detect_file_type_hex,"8":parse_elf_header,
                 "9":parse_pe_header,"10":extract_iocs,"11":xor_bruteforce_v2,
                 "12":scan_suspicious_apis,"13":detect_packer,"14":yara_scan,
                 "15":full_analysis}
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
    elif choice == "16":
        path = input("Enter file path: ").strip()
        print()
        print(analyze_file(path))
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()