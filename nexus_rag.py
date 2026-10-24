"""
NEXUS-RE RAG Service
Phase 5 - Retrieval-Augmented Generation over CVE + docs
Pure-Python fallback (no FAISS/Chroma dependency)
"""

import os
import re
import math
import json
from typing import List, Dict, Tuple
from collections import Counter


# ============================================================
#                    KNOWLEDGE BASE
# ============================================================

# Curated knowledge entries (would normally be loaded from CVE/docs)
KNOWLEDGE_BASE = [
    {
        "id": "CVE-2021-44228",
        "title": "Log4Shell - Remote Code Execution",
        "content": "Apache Log4j2 JNDI features used in configuration, log messages, and parameters do not protect against attacker-controlled LDAP and other JNDI related endpoints. An attacker who can control log messages can execute arbitrary code loaded from LDAP servers.",
        "tags": ["rce", "log4j", "java", "jndi", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2022-22965",
        "title": "Spring4Shell - RCE in Spring Framework",
        "content": "A Spring MVC or Spring WebFlux application running on JDK 9+ may be vulnerable to remote code execution via data binding.",
        "tags": ["rce", "spring", "java", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2017-0144",
        "title": "EternalBlue - SMBv1 RCE",
        "content": "The SMBv1 server in Microsoft Windows allows remote attackers to execute arbitrary code via crafted packets (MS17-010).",
        "tags": ["smb", "windows", "rce", "ransomware", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "MITRE-T1055",
        "title": "Process Injection",
        "content": "Adversaries may inject code into processes to evade process-based defenses and possibly elevate privileges. Common techniques include DLL injection, process hollowing, thread local storage, and APC injection.",
        "tags": ["injection", "persistence", "privilege", "windows"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1056",
        "title": "Input Capture - Keylogging",
        "content": "Adversaries may use methods of capturing user input to obtain credentials. Keyloggers typically use Windows APIs such as GetAsyncKeyState and SetWindowsHookEx.",
        "tags": ["keylogger", "credentials", "windows", "spyware"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1486",
        "title": "Data Encrypted for Impact (Ransomware)",
        "content": "Adversaries may encrypt data on target systems to interrupt availability. Ransomware notes often contain phrases like 'your files have been encrypted' and demand cryptocurrency payment.",
        "tags": ["ransomware", "encryption", "impact", "bitcoin"],
        "severity": "CRITICAL",
    },
    {
        "id": "MITRE-T1071",
        "title": "Application Layer Protocol (C2)",
        "content": "Adversaries may communicate using application layer protocols to avoid detection. Common patterns include HTTP(S) to bot.php or gate.php endpoints.",
        "tags": ["c2", "botnet", "http", "command-and-control"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1496",
        "title": "Resource Hijacking (Cryptomining)",
        "content": "Adversaries may leverage resources of compromised systems for cryptocurrency mining. Common miners include XMRig, and they often connect to stratum+tcp:// pools.",
        "tags": ["miner", "cryptomining", "monero", "resource"],
        "severity": "HIGH",
    },
    {
        "id": "PACKER-UPX",
        "title": "UPX Packer",
        "content": "UPX is a free, open-source executable packer. While legitimate, it is often used by malware to obfuscate code. UPX signatures include 'UPX0' and 'UPX1'.",
        "tags": ["packer", "upx", "obfuscation"],
        "severity": "MEDIUM",
    },
    {
        "id": "PACKER-THEMIDA",
        "title": "Themida Packer",
        "content": "Themida is a commercial protector known for strong anti-debugging and virtualization. Frequently used by advanced malware.",
        "tags": ["packer", "themida", "anti-debug", "commercial"],
        "severity": "HIGH",
    },
    {
        "id": "RE-GHIDRA",
        "title": "Ghidra Headless Mode",
        "content": "Ghidra can be run in headless mode via analyzeHeadless for automated binary analysis, decompilation, and function extraction.",
        "tags": ["ghidra", "headless", "decompiler", "tool"],
        "severity": "INFO",
    },
    {
        "id": "RE-FRIDA",
        "title": "Frida Dynamic Instrumentation",
        "content": "Frida allows injecting JavaScript into running processes for hooking, tracing, and modifying behavior at runtime.",
        "tags": ["frida", "dynamic", "hooking", "instrumentation"],
        "severity": "INFO",
    },

    {
        "id": "CVE-2014-0160",
        "title": "Heartbleed - OpenSSL Memory Leak",
        "content": "A vulnerability in the OpenSSL cryptography library allows attackers to read portions of server memory, exposing passwords, private keys, and session tokens.",
        "tags": ["openssl", "memory-leak", "tls", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2014-6271",
        "title": "Shellshock - Bash Command Injection",
        "content": "A vulnerability in GNU Bash allows attackers to execute arbitrary commands via crafted environment variables.",
        "tags": ["bash", "command-injection", "rce", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2019-0708",
        "title": "BlueKeep - Remote Desktop RCE",
        "content": "A pre-authentication remote code execution vulnerability in Windows Remote Desktop Services (RDP).",
        "tags": ["rdp", "windows", "rce", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2020-1472",
        "title": "Zerologon - Netlogon Privilege Escalation",
        "content": "A vulnerability in Windows Netlogon allows attackers to gain domain administrator privileges.",
        "tags": ["netlogon", "windows", "privilege-escalation", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "CVE-2023-38408",
        "title": "OpenSSH PKCS#11 RCE",
        "content": "A vulnerability in OpenSSH's PKCS#11 support can allow remote code execution via forwarded SSH agents.",
        "tags": ["openssh", "rce", "linux", "critical"],
        "severity": "CRITICAL",
    },
    {
        "id": "MITRE-T1003",
        "title": "OS Credential Dumping",
        "content": "Adversaries may attempt to dump credentials from OS memory to obtain account login credentials, such as passwords, hashes, or Kerberos tickets (e.g., via Mimikatz, ProcDump).",
        "tags": ["credential-dumping", "mimikatz", "windows", "lateral-movement"],
        "severity": "CRITICAL",
    },
    {
        "id": "MITRE-T1027",
        "title": "Obfuscated Files or Information",
        "content": "Adversaries may obfuscate payloads (e.g., Base64, XOR, custom packers) to hide malicious content from detection.",
        "tags": ["obfuscation", "base64", "xor", "packer"],
        "severity": "MEDIUM",
    },
    {
        "id": "MITRE-T1041",
        "title": "Exfiltration Over C2 Channel",
        "content": "Adversaries may steal data by exfiltrating it over an existing command-and-control channel (e.g., HTTP/S, DNS tunneling).",
        "tags": ["exfiltration", "c2", "dns", "http"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1105",
        "title": "Ingress Tool Transfer",
        "content": "Adversaries may transfer tools or files (e.g., malware, scripts) from an external system to a compromised environment (e.g., via certutil, bitsadmin).",
        "tags": ["ingress", "tool-transfer", "malware-dropper"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1136",
        "title": "Create or Modify System Process",
        "content": "Adversaries may create or modify system-level processes to repeatedly execute malicious payloads (e.g., systemd services, launchd, Windows services).",
        "tags": ["persistence", "services", "systemd"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1547",
        "title": "Boot or Logon Autostart Execution",
        "content": "Adversaries may configure system settings to automatically execute malicious code during boot or logon (e.g., Run keys, startup folders, cron jobs).",
        "tags": ["persistence", "autostart", "registry", "cron"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1562",
        "title": "Impair Defenses",
        "content": "Adversaries may modify system defenses to disable or bypass them (e.g., disabling AV, firewalls, or logging).",
        "tags": ["defense-evasion", "av-bypass", "firewall"],
        "severity": "HIGH",
    },
    {
        "id": "MITRE-T1566",
        "title": "Phishing",
        "content": "Adversaries may send phishing messages via email, SMS, or social media to gain access to systems.",
        "tags": ["phishing", "email", "initial-access"],
        "severity": "MEDIUM",
    },
    {
        "id": "MITRE-T1078",
        "title": "Valid Accounts",
        "content": "Adversaries may use legitimate credentials to gain access to systems and evade detection.",
        "tags": ["valid-accounts", "credentials", "lateral-movement"],
        "severity": "MEDIUM",
    },
    {
        "id": "PACKER-ASPack",
        "title": "ASPack Packer",
        "content": "ASPack is a Windows executable packer commonly used by malware to compress and obfuscate binaries. Signature: '.aspack', '.adata'.",
        "tags": ["packer", "aspack", "windows", "obfuscation"],
        "severity": "MEDIUM",
    },
    {
        "id": "PACKER-VMProtect",
        "title": "VMProtect Packer",
        "content": "VMProtect is a commercial protector that virtualizes code, making it very difficult to reverse engineer. Signature: '.vmp0', '.vmp1'.",
        "tags": ["packer", "vmprotect", "virtualization", "commercial"],
        "severity": "HIGH",
    },
    {
        "id": "PACKER-MPRESS",
        "title": "MPRESS Packer",
        "content": "MPRESS is a free Windows packer. Signature: 'MPRESS1', 'MPRESS2'.",
        "tags": ["packer", "mpress", "windows"],
        "severity": "MEDIUM",
    },
    {
        "id": "PACKER-Enigma",
        "title": "Enigma Protector",
        "content": "Enigma Protector is a commercial software protection tool that adds anti-debugging and licensing. Frequently abused by malware.",
        "tags": ["packer", "enigma", "anti-debug", "commercial"],
        "severity": "HIGH",
    },
    {
        "id": "RE-RADARE2",
        "title": "radare2 Framework",
        "content": "radare2 is an open-source reverse engineering framework with a command-line interface, supporting many architectures and file formats.",
        "tags": ["radare2", "reverse-engineering", "tool"],
        "severity": "INFO",
    },
    {
        "id": "RE-JADX",
        "title": "JADX Decompiler",
        "content": "JADX is a Dex to Java decompiler for Android APK analysis, useful for extracting the manifest and class files.",
        "tags": ["jadx", "android", "apk", "decompiler"],
        "severity": "INFO",
    },
]


# ============================================================
#                    TOKENIZER (simple)
# ============================================================

def tokenize(text: str) -> List[str]:
    """Convert text to lowercase word tokens."""
    text = text.lower()
    return re.findall(r'\b[a-z0-9_]{2,}\b', text)


# ============================================================
#                    TF-IDF SEARCH
# ============================================================

class TFIDFIndex:
    """Simple TF-IDF index for knowledge retrieval."""

    def __init__(self, documents: List[Dict]):
        self.documents = documents
        self.df = Counter()
        self.tokenized = []
        self._build_index()

    def _build_index(self):
        for doc in self.documents:
            tokens = tokenize(doc["title"] + " " + doc["content"] + " " + " ".join(doc.get("tags", [])))
            self.tokenized.append(tokens)
            for token in set(tokens):
                self.df[token] += 1

    def _idf(self, token: str) -> float:
        n = len(self.documents)
        df = self.df.get(token, 0)
        return math.log((n + 1) / (df + 1)) + 1

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Return top-k documents most similar to the query."""
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        results = []
        for i, doc in enumerate(self.documents):
            doc_tokens = self.tokenized[i]
            doc_counter = Counter(doc_tokens)

            score = 0.0
            for qt in q_tokens:
                if qt in doc_counter:
                    tf = doc_counter[qt] / len(doc_tokens)
                    idf = self._idf(qt)
                    score += tf * idf

            if score > 0:
                results.append((doc, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


# ============================================================
#                      RAG SERVICE
# ============================================================

class RAGService:
    """Retrieval-Augmented Generation service."""

    def __init__(self):
        self.index = TFIDFIndex(KNOWLEDGE_BASE)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find the most relevant knowledge entries for a query."""
        results = self.index.search(query, top_k)
        return [
            {
                "id": doc["id"],
                "title": doc["title"],
                "severity": doc["severity"],
                "snippet": doc["content"][:200] + ("..." if len(doc["content"]) > 200 else ""),
                "score": round(score, 3),
            }
            for doc, score in results
        ]

    def explain(self, evidence_text: str) -> str:
        """Ground a piece of evidence in retrieved knowledge."""
        results = self.retrieve(evidence_text, top_k=3)
        if not results:
            return "No relevant knowledge found."

        lines = ["Knowledge grounding:"]
        for r in results:
            lines.append(f"  [{r['id']}] {r['title']} (severity: {r['severity']})")
            lines.append(f"    {r['snippet']}")
            lines.append(f"    (relevance: {r['score']})")
        return "\n".join(lines)

    def stats(self) -> str:
        return f"Knowledge base: {len(KNOWLEDGE_BASE)} entries, {len(self.index.df)} unique terms"


# ============================================================
#                          CLI
# ============================================================

def main():
    print("=" * 65)
    print("  NEXUS-RE RAG Service v1.0")
    print("  Phase 5 - Retrieval-Augmented Generation")
    print("=" * 65)
    print()

    service = RAGService()
    print(service.stats())
    print()

    while True:
        query = input("Ask a question (or 'exit'): ").strip()
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        if not query:
            continue

        results = service.retrieve(query, top_k=3)
        if not results:
            print("  No relevant knowledge found.")
        else:
            print()
            for r in results:
                print(f"  [{r['id']}] {r['title']}")
                print(f"    Severity: {r['severity']}")
                print(f"    {r['snippet']}")
                print(f"    Score: {r['score']}")
                print()


if __name__ == "__main__":
    main()