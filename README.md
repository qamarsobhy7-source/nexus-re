# NEXUS-RE

> **AI-Powered Reverse Engineering & Security Analysis Platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/status-active-success)](.)

## What is NEXUS-RE?

NEXUS-RE is an open-source platform that bridges **Large Language Model (LLM) agents** with **professional reverse engineering tools** through the Model Context Protocol (MCP). It automates binary analysis, detects threats, and produces evidence-backed reports — without requiring source code.

## Features

### Core Analysis Tools (16)
- **Basic**: Hex dump, string extraction, SHA256/MD5 hashing, Shannon entropy
- **File Format**: ELF header parser, PE header parser, magic-number detection
- **Threat Detection**: IOC extraction, suspicious Windows API scanner, packer detection (UPX/ASPack/VMProtect/Themida)
- **Cryptanalysis**: Single-byte XOR brute-force with English frequency scoring
- **Rule Matching**: YARA-style malware pattern scanner
- **Composite**: Full binary analysis + file-path analysis

### Advanced Features (Roadmap)
- Multi-agent orchestration (LangGraph + ReAct)
- RAG grounding over CVE + Ghidra/Frida documentation
- Bilingual UI (Arabic/English)
- Explainable AI (SHAP/LIME + tool traces)
- Dynamic analysis (Frida + strace)
- Docker deployment + public live demo

## Quick Start

### Requirements
- Python 3.11 or higher
- (Optional) `mcp` package for AI agent integration

### Run the toolkit

```bash
python nexus_re_v2.py