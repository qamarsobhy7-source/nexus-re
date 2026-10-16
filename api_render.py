"""
NEXUS-RE REST API - Render Deployment Version
Pure Python HTTP Server with CORS + PORT support
"""

import importlib.util
import json
import os
import sys
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        # CORS headers for GitHub Pages
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
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

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path in ("/", "/health"):
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
                {"id": i, "name": name}
                for i, name in enumerate([
                    "hex_dump", "extract_strings", "calculate_hash",
                    "calculate_entropy", "file_info", "detect_file_type",
                    "detect_file_type_hex", "parse_elf_header", "parse_pe_header",
                    "extract_iocs", "xor_bruteforce", "xor_bruteforce_v2",
                    "scan_suspicious_apis", "detect_packer", "yara_scan",
                    "full_analysis", "analyze_file", "version_diff",
                    "section_analyzer", "base64_detector", "string_similarity",
                ], 1)
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
            # Basic tools
            if path == "/hex_dump":
                result = toolkit.hex_dump(body.get("text", ""))
            elif path == "/extract_strings":
                result = toolkit.extract_strings(body.get("text", ""))
            elif path == "/calculate_hash":
                result = toolkit.calculate_hash(body.get("text", ""))
            elif path == "/calculate_entropy":
                result = toolkit.calculate_entropy(body.get("text", ""))
            elif path == "/file_info":
                result = toolkit.file_info(body.get("text", ""))

            # Binary tools
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

            # Advanced tools
            elif path == "/full_analysis":
                result = toolkit.full_analysis(body.get("hex_string", ""))
            elif path == "/analyze_file":
                result = toolkit.analyze_file(body.get("path", ""))
            elif path == "/version_diff":
                result = toolkit.version_diff(body.get("hex1", ""), body.get("hex2", ""))
            elif path == "/section_analyzer":
                result = toolkit.section_analyzer(body.get("hex_string", ""))
            elif path == "/base64_detector":
                result = toolkit.base64_detector(body.get("hex_string", ""))
            elif path == "/string_similarity":
                result = toolkit.string_similarity(body.get("text1", ""), body.get("text2", ""))

            # Multi-Agent
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
#                    SERVER LAUNCHER (Render-compatible)
# ============================================================

def run_server():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"[SERVER] NEXUS-RE API running on http://{host}:{port}")
    print(f"[SERVER] Toolkit:  {'LOADED' if toolkit else 'FAILED'}")
    print(f"[SERVER] Agents:   {'LOADED' if agents_mod else 'FAILED'}")
    print(f"[SERVER] RAG:      {'LOADED' if rag_mod else 'FAILED'}")
    print(f"[SERVER] Endpoints: 24")
    print()
    
    server = HTTPServer((host, port), NexusAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")
        server.server_close()


if __name__ == "__main__":
    run_server()