"""
NEXUS-RE setup.py
Makes the toolkit pip-installable: pip install nexus-re
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "NEXUS-RE: AI-Powered Reverse Engineering Platform"

setup(
    name="nexus-re",
    version="3.0.0",
    author="Qamar Sobhy",
    author_email="",
    description="AI-Powered Reverse Engineering & Security Analysis Platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/qamarsobhy7-source/nexus-re",
    license="MIT",
    py_modules=[
        "nexus_re_v3",
        "nexus_re_server",
        "nexus_agents",
        "nexus_rag",
        "api",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Security",
        "Topic :: Software Development :: Disassemblers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "reverse-engineering",
        "malware-analysis",
        "binary-analysis",
        "security",
        "cybersecurity",
        "ai",
        "llm",
        "mcp",
        "multi-agent",
        "rag",
    ],
    extras_require={
        "agents": ["mcp>=2.3.0", "langgraph>=0.2.0", "langchain>=0.3.0"],
        "rag": ["faiss-cpu>=1.8.0", "chromadb>=0.5.0"],
        "api": ["fastapi>=0.115.0", "uvicorn>=0.32.0"],
        "dev": ["pytest>=8.0.0", "flake8>=7.0.0", "black>=24.0.0"],
    },
    entry_points={
        "console_scripts": [
            "nexus-re=nexus_re_v3:main",
            "nexus-agents=nexus_agents:main",
            "nexus-rag=nexus_rag:main",
        ],
    },
    zip_safe=False,
)