"""
NEXUS-RE: AI-Powered Reverse Engineering Platform
Pydroid 3 Edition - Complete Version
"""

import hashlib
import re
import math
import struct

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
        p = c / len(data)
        e -= p * math.log2(p)
    verdict = "HIGH (packed/encrypted)" if e > 7.0 else "MEDIUM" if e > 5.0 else "LOW (normal)"
    return f"Entropy: {e:.4f}\nVerdict: {verdict}"

def detect_file_type_hex(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    sigs = [(b'\x7fELF','ELF (Linux)'),(b'MZ','PE (Windows)'),
            (b'\x89PNG','PNG Image'),(b'PK\x03\x04','ZIP Archive'),
            (b'%PDF','PDF'),(b'\x1f\x8b\x08','GZIP')]
    for sig, name in sigs:
        if data.startswith(sig): return f"Type: {name}"
    return f"Unknown (magic: {data[:4].hex()})"

def extract_iocs(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore')
    urls = list(set(re.findall(r'https?://[^\s"\'<>]+', text)))
    ips = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)))
    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
    out = [f"Total IOCs: {len(urls)+len(ips)+len(emails)}"]
    if urls: out.append(f"URLs ({len(urls)}):"); [out.append(f"  - {u}") for u in urls[:5]]
    if ips: out.append(f"IPs ({len(ips)}):"); [out.append(f"  - {i}") for i in ips[:5]]
    if emails: out.append(f"Emails ({len(emails)}):"); [out.append(f"  - {e}") for e in emails[:5]]
    return "\n".join(out) if len(out) > 1 else "No IOCs found"

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
                'GetAsyncKeyState','SetWindowsHookEx','NtUnmapViewOfSection']
    high = ['VirtualAlloc','LoadLibrary','GetProcAddress','CreateProcess',
            'URLDownloadToFile','ShellExecute']
    found_c = [a for a in critical if a in text]
    found_h = [a for a in high if a in text]
    out = ["Suspicious API Scan:"]
    if found_c:
        out.append(f"THREAT: CRITICAL")
        out.append(f"  {', '.join(found_c)}")
    if found_h:
        out.append(f"THREAT: HIGH")
        out.append(f"  {', '.join(found_h)}")
    if not found_c and not found_h:
        out.append("No suspicious APIs detected")
    return "\n".join(out)

def detect_packer(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    packers = [(b'UPX0','UPX'),(b'UPX1','UPX'),(b'.aspack','ASPack'),
               (b'Themida','Themida'),(b'.vmp0','VMProtect'),(b'MPRESS1','MPRESS')]
    detected = []
    for sig, name in packers:
        if sig in data and name not in detected: detected.append(name)
    if detected:
        return f"PACKED: YES\nDetected: {', '.join(detected)}"
    return "PACKED: NO"

def yara_scan(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore').lower()
    rules = {
        'Ransomware': ['your files have been encrypted','bitcoin','decrypt','ransom'],
        'Keylogger': ['getasynckeystate','setwindowshookex'],
        'Credential Stealer': ['login data','cookies','wallet.dat'],
        'Crypto Miner': ['stratum+tcp://','xmrig','monero'],
        'Botnet C2': ['bot.php','gate.php','c2 server'],
        'Antivirus Evasion': ['stopdefender','disablerealtimemonitoring'],
        'Reverse Shell': ['/bin/sh','cmd.exe /c','reverse shell'],
    }
    matches = []
    for name, sigs in rules.items():
        found = [s for s in sigs if s in text]
        if found: matches.append(f"  [{name}]: {', '.join(found)}")
    if matches:
        return f"YARA: MALICIOUS ({len(matches)} rules)\n" + "\n".join(matches)
    return "YARA: Clean (no known patterns matched)"

def full_analysis(hex_string):
    try: data = bytes.fromhex(hex_string)
    except: return "Invalid hex"
    text = data.decode('utf-8', errors='ignore')
    out = ["=" * 50, "NEXUS-RE FULL ANALYSIS REPORT", "=" * 50, ""]
    out.append(f"Size: {len(data)} bytes")
    out.append(f"SHA256: {hashlib.sha256(data).hexdigest()}")
    out.append(f"MD5:    {hashlib.md5(data).hexdigest()}")
    out.append("")
    out.append("[FILE TYPE]")
    out.append(detect_file_type_hex(hex_string))
    out.append("")
    out.append("[ENTROPY]")
    out.append(calculate_entropy(data.decode('latin-1', errors='ignore')))
    out.append("")
    out.append("[IOCs]")
    out.append(extract_iocs(hex_string))
    out.append("")
    out.append("[APIs]")
    out.append(scan_suspicious_apis(hex_string))
    out.append("")
    out.append("[YARA]")
    out.append(yara_scan(hex_string))
    out.append("")
    out.append("=" * 50)
    return "\n".join(out)

def main():
    print("=" * 50)
    print("  NEXUS-RE v1.0 - Reverse Engineering Toolkit")
    print("=" * 50)
    print()
    print("1. Hex Dump (any text)")
    print("2. Extract Strings (any text)")
    print("3. Calculate Hash (any text)")
    print("4. Calculate Entropy (any text)")
    print("5. Detect File Type (hex input)")
    print("6. Extract IOCs (hex input)")
    print("7. XOR Brute Force (hex input)")
    print("8. Scan Suspicious APIs (hex input)")
    print("9. Detect Packer (hex input)")
    print("10. YARA Scan (hex input)")
    print("11. Full Analysis (hex input)")
    print("0. Exit")
    print()
    choice = input("Choose (0-11): ").strip()
    if choice == "0":
        print("Goodbye!")
        return
    print()
    text = input("Enter input: ").strip()
    print()
    tools = {
        "1": hex_dump,
        "2": extract_strings,
        "3": calculate_hash,
        "4": calculate_entropy,
        "5": detect_file_type_hex,
        "6": extract_iocs,
        "7": xor_bruteforce_v2,
        "8": scan_suspicious_apis,
        "9": detect_packer,
        "10": yara_scan,
        "11": full_analysis,
    }
    if choice in tools:
        print("=" * 50)
        print(tools[choice](text))
        print("=" * 50)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()