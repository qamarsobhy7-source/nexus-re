"""
NEXUS-RE REST API
Phase 7 - Pure Python HTTP Server (no dependencies)
"""

import importlib.util
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime


# ============================================================
#                    LOAD TOOLKIT
# ============================================================

def load_toolkit():
    try:
        spec = importlib.util.spec_from_file_location("nexus_re_v3", "nexus_re_v3.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[ERROR] Could not load toolkit: {e}")
        return None


def load_module(name, path):
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[WARN] Could not load {name}: {e}")
        return None


toolkit = load_toolkit()
agents_mod = load_module("nexus_agents", "nexus_agents.py")
rag_mod = load_module("nexus_rag", "nexus_rag.py")


# ============================================================
#                    REQUEST HANDLER
# ============================================================

class NexusAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Custom logging
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode('utf-8')
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/" or path == "/health":
            self._send_json({
                "name": "NEXUS-RE API",
                "version": "3.0.0",
                "status": "running",
                "toolkit_loaded": toolkit is not None,
                "agents_loaded": agents_mod is not None,
                "rag_loaded": rag_mod is not None,
                "timestamp": datetime.now().isoformat(),
            })

        elif path == "/tools":
            tools = [
                {"id": 1, "name": "hex_dump", "category": "basic"},
                {"id": 2, "name": "extract_strings", "category": "basic"},
                {"id": 3, "name": "calculate_hash", "category": "basic"},
                {"id": 4, "name": "calculate_entropy", "category": "basic"},
                {"id": 5, "name": "detect_file_type", "category": "basic"},
                {"id": 6, "name": "file_info", "category": "basic"},
                {"id": 7, "name": "detect_file_type_hex", "category": "binary"},
                {"id": 8, "name": "parse_elf_header", "category": "binary"},
                {"id": 9, "name": "parse_pe_header", "category": "binary"},
                {"id": 10, "name": "extract_iocs", "category": "threat"},
                {"id": 11, "name": "xor_bruteforce", "category": "crypto"},
                {"id": 12, "name": "xor_bruteforce_v2", "category": "crypto"},
                {"id": 13, "name": "scan_suspicious_apis", "category": "threat"},
                {"id": 14, "name": "detect_packer", "category": "threat"},
                {"id": 15, "name": "yara_scan", "category": "threat"},
                {"id": 16, "name": "full_analysis", "category": "composite"},
                {"id": 17, "name": "analyze_file", "category": "composite"},
                {"id": 18, "name": "version_diff", "category": "advanced"},
                {"id": 19, "name": "section_analyzer", "category": "advanced"},
                {"id": 20, "name": "base64_detector", "category": "advanced"},
                {"id": 21, "name": "string_similarity", "category": "advanced"},
            ]
            self._send_json({"count": len(tools), "tools": tools})

        elif path == "/rag/search":
            q = params.get("q", [""])[0]
            if not q or not rag_mod:
                self._send_json({"error": "Missing q or RAG not loaded"}, 400)
                return
            service = rag_mod.RAGService()
            results = service.retrieve(q, top_k=3)
            self._send_json({"query": q, "results": results})

        else:
            self._send_json({"error": "Not found", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        if not toolkit:
            self._send_json({"error": "Toolkit not loaded"}, 500)
            return

        try:
            # ----- Basic tools -----
            if path == "/hex_dump":
                result = toolkit.hex_dump(body.get("text", ""))
            elif path == "/extract_strings":
                result = toolkit.extract_strings(body.get("text", ""))
            elif path == "/calculate_hash":
                result = toolkit.calculate_hash(body.get("text", ""))
            elif path == "/calculate_entropy":
                result = toolkit.calculate_entropy(body.get("text", ""))

            # ----- Binary tools -----
            elif path == "/detect_file_type":
                result = toolkit.detect_file_type_hex(body.get("hex_string", ""))
            elif path == "/parse_elf":
                result = toolkit.parse_elf_header(body.get("hex_string", ""))
            elif path == "/parse_pe":
                result = toolkit.parse_pe_header(body.get("hex_string", ""))
            elif path == "/extract_iocs":
                result = toolkit.extract_iocs(body.get("hex_string", ""))
            elif path == "/xor_bruteforce":
                result = toolkit.xor_bruteforce(body.get("hex_string", ""))
            elif path == "/xor_bruteforce_v2":
                result = toolkit.xor_bruteforce_v2(body.get("hex_string", ""))
            elif path == "/scan_apis":
                result = toolkit.scan_suspicious_apis(body.get("hex_string", ""))
            elif path == "/detect_packer":
                result = toolkit.detect_packer(body.get("hex_string", ""))
            elif path == "/yara_scan":
                result = toolkit.yara_scan(body.get("hex_string", ""))

            # ----- Composite -----
            elif path == "/full_analysis":
                result = toolkit.full_analysis(body.get("hex_string", ""))
            elif path == "/analyze_file":
                result = toolkit.analyze_file(body.get("path", ""))

            # ----- Advanced -----
            elif path == "/version_diff":
                result = toolkit.version_diff(body.get("hex1", ""), body.get("hex2", ""))
            elif path == "/section_analyzer":
                result = toolkit.section_analyzer(body.get("hex_string", ""))
            elif path == "/base64_detector":
                result = toolkit.base64_detector(body.get("hex_string", ""))
            elif path == "/string_similarity":
                result = toolkit.string_similarity(body.get("text1", ""), body.get("text2", ""))

            # ----- Agents -----
            elif path == "/agents/analyze":
                if not agents_mod:
                    self._send_json({"error": "Agents module not loaded"}, 500)
                    return
                orch = agents_mod.Orchestrator(toolkit)
                state = orch.run(body.get("target", ""))
                self._send_json({
                    "session_id": state.session_id,
                    "verdict": state.verdict,
                    "evidence_count": len(state.evidence),
                    "report": state.final_report,
                })
                return

            else:
                self._send_json({"error": "Not found", "path": path}, 404)
                return

            self._send_json({"result": result})

        except Exception as e:
            self._send_json({"error": str(e)}, 500)


# ============================================================
#                    STANDALONE TEST
# ============================================================

def test_standalone():
    print("=" * 65)
    print("  NEXUS-RE API - Standalone Self-Test")
    print("=" * 65)
    print()
    print(f"[{'OK' if toolkit else 'FAIL'}] Toolkit loaded")
    print(f"[{'OK' if agents_mod else 'FAIL'}] Agents module loaded")
    print(f"[{'OK' if rag_mod else 'FAIL'}] RAG module loaded")
    print()

    if toolkit:
        tests = [
            ("hex_dump('NEXUS')", lambda: toolkit.hex_dump("NEXUS")),
            ("calculate_hash('NEXUS')", lambda: toolkit.calculate_hash("NEXUS")),
            ("detect_file_type_hex('7f454c46')", lambda: toolkit.detect_file_type_hex("7f454c46")),
        ]
        for name, fn in tests:
            try:
                result = fn()
                first_line = result.split("\n")[0][:60]
                print(f"  [PASS] {name}")
                print(f"         {first_line}")
            except Exception as e:
                print(f"  [FAIL] {name}: {e}")
    print()

    print("To start the server:")
    print("  python api.py")
    print()
    print("Then test with:")
    print("  curl http://localhost:8000/health")
    print("  curl http://localhost:8000/tools")
    print("=" * 65)


# ============================================================
#                    SERVER LAUNCHER
# ============================================================

def run_server(port=8000):
    server = HTTPServer(("0.0.0.0", port), NexusAPIHandler)
    print(f"[SERVER] NEXUS-RE API running on http://0.0.0.0:{port}")
    print(f"[SERVER] Endpoints:")
    print(f"  GET  /health")
    print(f"  GET  /tools")
    print(f"  GET  /rag/search?q=ransomware")
    print(f"  POST /hex_dump {{text: 'NEXUS'}}")
    print(f"  POST /full_analysis {{hex_string: '7f454c46...'}}")
    print(f"  POST /agents/analyze {{target: 'hex_or_path'}}")
    print(f"[SERVER] Press Ctrl+C to stop")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")
        server.server_close()


# ============================================================
#                    ENTRY POINT
# ============================================================

if __name__ == "__main__":
    test_standalone()
    print()
    answer = input("Start server? (y/n): ").strip().lower()
    if answer == "y":
        run_server()