#!/usr/bin/env python3
"""
NEXUS-RE Doctor
Environment health check for NEXUS-RE
"""

import os
import sys
import platform
import importlib.util


def check_mark(ok):
    return "✅" if ok else "❌"


def check_optional(ok):
    return "✅" if ok else "⚠️ "


def main():
    print("=" * 65)
    print("  NEXUS-RE Doctor v1.0")
    print("  Environment Health Check")
    print("=" * 65)
    print()

    issues = 0

    # 1. System Info
    print("[1] SYSTEM INFORMATION")
    print("-" * 65)
    print(f"  {check_mark(True)} OS:          {platform.system()} {platform.release()}")
    print(f"  {check_mark(True)} Machine:     {platform.machine()}")
    print(f"  {check_mark(True)} Python:      {sys.version.split()[0]}")
    print(f"  {check_mark(True)} Executable:  {sys.executable}")
    print()

    # 2. Python Version
    print("[2] PYTHON VERSION CHECK")
    print("-" * 65)
    major, minor = sys.version_info[:2]
    py_ok = (major == 3 and minor >= 11)
    print(f"  {check_mark(py_ok)} Python {major}.{minor} (need 3.11+)")
    if not py_ok:
        print("  ⚠️  Please upgrade Python to 3.11 or higher")
        issues += 1
    print()

    # 3. Required Files
    print("[3] REQUIRED FILES")
    print("-" * 65)
    required_files = [
        "nexus_re_v3.py",
        "nexus_agents.py",
        "nexus_rag.py",
    ]
    base_paths = [
        os.getcwd(),
        "/storage/emulated/0/",
        "/storage/emulated/0/Documents/",
        "/storage/emulated/0/Documents/src/tools/",
    ]
    
    for f in required_files:
        found = False
        for base in base_paths:
            if os.path.exists(os.path.join(base, f)):
                found = True
                break
        print(f"  {check_mark(found)} {f}")
        if not found:
            issues += 1
    print()

    # 4. Optional Files
    print("[4] OPTIONAL FILES")
    print("-" * 65)
    optional_files = [
        "README.md",
        "proposal.md",
        "LICENSE",
        "Dockerfile",
        "requirements.txt",
    ]
    for f in optional_files:
        found = any(os.path.exists(os.path.join(b, f)) for b in base_paths)
        print(f"  {check_optional(found)} {f}")
    print()

    # 5. Module Import Test
    print("[5] MODULE IMPORT TEST")
    print("-" * 65)
    
    toolkit_path = None
    for base in base_paths:
        p = os.path.join(base, "nexus_re_v3.py")
        if os.path.exists(p):
            toolkit_path = p
            break
    
    if toolkit_path:
        try:
            spec = importlib.util.spec_from_file_location("nexus_re_v3", toolkit_path)
            toolkit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(toolkit)
            print(f"  {check_mark(True)} nexus_re_v3.py loaded successfully")
            
            tools = [name for name in dir(toolkit) if callable(getattr(toolkit, name)) and not name.startswith('_')]
            print(f"  {check_mark(True)} Tools detected: {len(tools)}")
        except Exception as e:
            print(f"  {check_mark(False)} nexus_re_v3.py failed to load: {e}")
            issues += 1
    else:
        print(f"  {check_mark(False)} nexus_re_v3.py not found")
        issues += 1
    print()

    # 6. Optional Dependencies
    print("[6] OPTIONAL DEPENDENCIES")
    print("-" * 65)
    
    optional_deps = {
        "mcp": "MCP Server support",
        "requests": "HTTP requests",
        "huggingface_hub": "Hugging Face uploads",
        "fastapi": "FastAPI server (alternative)",
        "uvicorn": "ASGI server (alternative)",
    }
    for dep, desc in optional_deps.items():
        try:
            __import__(dep)
            print(f"  {check_optional(True)} {dep:<20} ({desc})")
        except ImportError:
            print(f"  {check_optional(False)} {dep:<20} ({desc})")
    print()

    # 7. Network Check
    print("[7] NETWORK CONNECTIVITY")
    print("-" * 65)
    try:
        import urllib.request
        urllib.request.urlopen("https://github.com", timeout=5)
        print(f"  {check_mark(True)} Internet connection: OK")
    except Exception:
        print(f"  {check_mark(False)} Internet connection: FAILED")
        print("  ⚠️  Some features may not work offline")
    print()

    # 8. Storage Check
    print("[8] STORAGE")
    print("-" * 65)
    try:
        import shutil
        total, used, free = shutil.disk_usage("/storage/emulated/0/")
        free_gb = free / (1024**3)
        print(f"  {check_mark(free_gb > 0.5)} Free space: {free_gb:.2f} GB")
        if free_gb < 0.5:
            print("  ⚠️  Low disk space")
    except Exception as e:
        print(f"  {check_optional(False)} Could not check storage: {e}")
    print()

    # Summary
    print("=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    if issues == 0:
        print(f"  {check_mark(True)} All critical checks passed!")
        print("  ✅ NEXUS-RE is ready to use.")
    else:
        print(f"  {check_mark(False)} {issues} issue(s) found.")
        print("  ⚠️  Please fix them before running the toolkit.")
    print()
    print("  For help: https://github.com/qamarsobhy7-source/nexus-re")
    print("=" * 65)


if __name__ == "__main__":
    main()