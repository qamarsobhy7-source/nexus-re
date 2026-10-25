"""
NEXUS-RE setup.py — compatibility shim

All package metadata is defined in `pyproject.toml` (PEP 621).
This file exists only for backward compatibility with tools that
still call `python setup.py ...`.

Do NOT add dependencies or metadata here — edit pyproject.toml instead.
"""

from setuptools import setup

setup()
