# NEXUS-RE REST API Reference

> Complete guide to all 24 API endpoints with curl examples.

---

## Base URL

```
Local:      http://localhost:8000
Production: https://qamar-sobhy-nexus-re-api.hf.space
```

---

## Authentication

The API supports **optional** API key authentication.

### Setup

```bash
export NEXUS_API_KEY="your-secret-key-here"
python api_render.py
```

### Using the Key

```bash
curl -H "X-API-Key: your-secret-key-here" \
     http://localhost:8000/hex_dump
```

### Public Endpoints (No Auth)

- `GET /`
- `GET /health`
- `GET /tools`

> **Note:** If `NEXUS_API_KEY` is not set, auth is disabled (dev mode).

---

## Health & Info

### `GET /health`

Returns server health status.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "name": "NEXUS-RE API",
  "version": "3.0.0",
  "status": "running",
  "toolkit_loaded": true,
  "agents_loaded": true,
  "rag_loaded": true
}
```

### `GET /tools`

Lists all 31 analysis tools.

```bash
curl http://localhost:8000/tools
```

---

## Basic Tools

### `POST /hex_dump`

Convert text to hexadecimal.

```bash
curl -X POST http://localhost:8000/hex_dump \
     -H "Content-Type: application/json" \
     -d '{"text": "NEXUS"}'
```

**Response:**
`{"result": "Size: 5 bytes\nHex: 4e45585553"}`

### `POST /calculate_hash`

```bash
curl -X POST http://localhost:8000/calculate_hash \
     -H "Content-Type: application/json" \
     -d '{"text": "NEXUS"}'
```

### `POST /calculate_entropy`

```bash
curl -X POST http://localhost:8000/calculate_entropy \
     -H "Content-Type: application/json" \
     -d '{"text": "NEXUS-RE"}'
```

---

## Binary Tools

### `POST /detect_file_type`

```bash
curl -X POST http://localhost:8000/detect_file_type \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "7f454c46"}'
```

**Response:**
`{"result": "Type: ELF (Linux)\nConfidence: HIGH"}`

### `POST /parse_elf`

```bash
curl -X POST http://localhost:8000/parse_elf \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "7f454c4602010100000000000000000002003e00"}'
```

### `POST /parse_pe`

```bash
curl -X POST http://localhost:8000/parse_pe \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "4d5a9000..."}'
```

### `POST /extract_iocs`

Extracts URLs, IPs, emails, registry keys, file paths.

```bash
curl -X POST http://localhost:8000/extract_iocs \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "687474703a2f2f6578616d706c652e636f6d"}'
```

### `POST /xor_bruteforce_v2`

```bash
curl -X POST http://localhost:8000/xor_bruteforce_v2 \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "162a2b31622b3162"}'
```

### `POST /scan_apis`

```bash
curl -X POST http://localhost:8000/scan_apis \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "43726561746552656d6f7465546872656164"}'
```

### `POST /detect_packer`

```bash
curl -X POST http://localhost:8000/detect_packer \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "55505830"}'
```

### `POST /yara_scan`

```bash
curl -X POST http://localhost:8000/yara_scan \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "626974636f696e"}'
```

---

## Advanced Tools

### `POST /full_analysis`

Runs all core tools and returns a complete report.

```bash
curl -X POST http://localhost:8000/full_analysis \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "7f454c4602010100"}'
```

### `POST /analyze_file`

Analyzes a file on disk by path.

```bash
curl -X POST http://localhost:8000/analyze_file \
     -H "Content-Type: application/json" \
     -d '{"path": "/samples/suspicious.exe"}'
```

### `POST /version_diff`

```bash
curl -X POST http://localhost:8000/version_diff \
     -H "Content-Type: application/json" \
     -d '{"hex1": "4e45585553", "hex2": "4e45585853"}'
```

### `POST /section_analyzer`

```bash
curl -X POST http://localhost:8000/section_analyzer \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "4142..."}'
```

### `POST /base64_detector`

```bash
curl -X POST http://localhost:8000/base64_detector \
     -H "Content-Type: application/json" \
     -d '{"hex_string": "5347567362473867526b56535656303d"}'
```

### `POST /string_similarity`

```bash
curl -X POST http://localhost:8000/string_similarity \
     -H "Content-Type: application/json" \
     -d '{"text1": "NEXUS", "text2": "NEXUS-RE"}'
```

---

## AI Agents & RAG

### `POST /agents/analyze`

Runs all 4 agents (Static, Security, Crypto, Report) on the target.

```bash
curl -X POST http://localhost:8000/agents/analyze \
     -H "Content-Type: application/json" \
     -d '{"target": "7f454c4602010100"}'
```

**Response:**
`{"session_id": "...", "verdict": "UNKNOWN", "evidence_count": 6, "report": "..."}`

### `GET /rag/search`

Searches the 32-entry knowledge base.

```bash
curl "http://localhost:8000/rag/search?q=ransomware+bitcoin"
```

**Response:**
`{"query": "ransomware bitcoin", "results": [{"id": "MITRE-T1486", "title": "Data Encrypted for Impact", ...}]}`

---

## Error Codes

| Code | Meaning |
|:----:|---------|
| 200 | Success |
| 400 | Bad Request (invalid JSON or missing field) |
| 401 | Unauthorized (invalid API key) |
| 404 | Endpoint not found |
| 500 | Internal server error |

---

## Rate Limiting

**Currently: None.** The API is designed for local use and educational purposes.
For production, add rate limiting via reverse proxy (nginx, Cloudflare).

---

## Support

- **Issues:** [GitHub Issues](https://github.com/qamarsobhy7-source/nexus-re/issues)
- **Live Demo:** https://qamar-sobhy-nexus-re-api.static.hf.space
