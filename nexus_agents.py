"""
NEXUS-RE Multi-Agent Orchestration System
Phase 4 - Custom ReAct Orchestrator
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================
#                        CORE TYPES
# ============================================================

@dataclass
class Evidence:
    """A single piece of evidence collected during analysis."""
    tool: str
    result: str
    confidence: str  # HIGH, MEDIUM, LOW
    artifact: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "result": self.result,
            "confidence": self.confidence,
            "artifact": self.artifact,
            "timestamp": self.timestamp,
        }


@dataclass
class AnalysisState:
    """Shared state across all agents in a session."""
    target: str
    session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    evidence: List[Evidence] = field(default_factory=list)
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    final_report: str = ""
    verdict: str = "UNKNOWN"

    def add_evidence(self, tool: str, result: str, confidence: str, artifact: str = None):
        self.evidence.append(Evidence(tool, result, confidence, artifact))

    def summary(self) -> str:
        return f"Session {self.session_id} | {len(self.evidence)} evidence pieces | verdict: {self.verdict}"


# ============================================================
#                       TOOL LOADER
# ============================================================

def load_toolkit():
    """Load the NEXUS-RE toolkit (nexus_re_v3.py)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("nexus_re_v3", "nexus_re_v3.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[WARN] Could not load toolkit: {e}")
        return None


# ============================================================
#                       BASE AGENT
# ============================================================

class BaseAgent:
    """Base class for all specialist agents."""
    name = "base"
    role = "Generic agent"

    def __init__(self, toolkit):
        self.toolkit = toolkit

    def can_handle(self, state: AnalysisState) -> bool:
        """Whether this agent can contribute to the current state."""
        return True

    def act(self, state: AnalysisState) -> AnalysisState:
        """Perform this agent's contribution to the state."""
        raise NotImplementedError

    def describe(self) -> str:
        return f"{self.name}: {self.role}"


# ============================================================
#                     SPECIALIST AGENTS
# ============================================================

class StaticAgent(BaseAgent):
    """Performs static binary analysis using core tools."""
    name = "static"
    role = "Static binary analysis (ELF, PE, entropy, strings)"

    def act(self, state: AnalysisState) -> AnalysisState:
        if not self.toolkit:
            return state

        hex_data = self._read_target(state.target)
        if not hex_data:
            state.add_evidence("static", "Failed to read target", "LOW")
            return state

        # File type
        ftype = self.toolkit.detect_file_type_hex(hex_data)
        state.add_evidence("detect_file_type_hex", ftype, "HIGH")

        # Entropy
        try:
            data_bytes = bytes.fromhex(hex_data)
            entropy_result = self.toolkit.calculate_entropy(
                data_bytes.decode('latin-1', errors='ignore')
            )
            state.add_evidence("calculate_entropy", entropy_result, "HIGH")
        except Exception:
            pass

        # ELF/PE parsing
        if "ELF" in ftype:
            elf = self.toolkit.parse_elf_header(hex_data)
            state.add_evidence("parse_elf_header", elf, "HIGH")
        elif "PE" in ftype:
            pe = self.toolkit.parse_pe_header(hex_data)
            state.add_evidence("parse_pe_header", pe, "HIGH")

        return state

    def _read_target(self, path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read().hex()
            # Assume it's already hex
            bytes.fromhex(path)
            return path
        except Exception:
            return None


class SecurityAgent(BaseAgent):
    """Detects threats: IOCs, suspicious APIs, packers, YARA patterns."""
    name = "security"
    role = "Threat detection (IOCs, APIs, packers, YARA)"

    def act(self, state: AnalysisState) -> AnalysisState:
        if not self.toolkit:
            return state

        hex_data = self._read_target(state.target)
        if not hex_data:
            return state

        # IOCs
        iocs = self.toolkit.extract_iocs(hex_data)
        if "No IOCs" not in iocs:
            state.add_evidence("extract_iocs", iocs, "HIGH")

        # Suspicious APIs
        apis = self.toolkit.scan_suspicious_apis(hex_data)
        if "No suspicious" not in apis:
            state.add_evidence("scan_suspicious_apis", apis, "HIGH")
            if "CRITICAL" in apis:
                state.verdict = "MALICIOUS"

        # Packer detection
        packer = self.toolkit.detect_packer(hex_data)
        state.add_evidence("detect_packer", packer, "HIGH")

        # YARA
        yara = self.toolkit.yara_scan(hex_data)
        state.add_evidence("yara_scan", yara, "HIGH")
        if "MALICIOUS" in yara:
            state.verdict = "MALICIOUS"

        return state

    def _read_target(self, path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read().hex()
            bytes.fromhex(path)
            return path
        except Exception:
            return None


class CryptoAgent(BaseAgent):
    """Handles XOR brute-force and Base64 detection."""
    name = "crypto"
    role = "Cryptanalysis (XOR, Base64)"

    def act(self, state: AnalysisState) -> AnalysisState:
        if not self.toolkit:
            return state

        hex_data = self._read_target(state.target)
        if not hex_data:
            return state

        # Base64 detector
        b64 = self.toolkit.base64_detector(hex_data)
        if "No Base64" not in b64:
            state.add_evidence("base64_detector", b64, "MEDIUM")

        # XOR brute-force
        xor = self.toolkit.xor_bruteforce_v2(hex_data)
        state.add_evidence("xor_bruteforce_v2", xor, "MEDIUM")

        return state

    def _read_target(self, path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read().hex()
            bytes.fromhex(path)
            return path
        except Exception:
            return None


class ReportAgent(BaseAgent):
    """Compiles all evidence into a final report."""
    name = "report"
    role = "Evidence synthesis and report generation"

    def act(self, state: AnalysisState) -> AnalysisState:
        lines = []
        lines.append("=" * 65)
        lines.append("  NEXUS-RE MULTI-AGENT ANALYSIS REPORT")
        lines.append("=" * 65)
        lines.append(f"  Session:     {state.session_id}")
        lines.append(f"  Target:      {state.target}")
        lines.append(f"  Verdict:     {state.verdict}")
        lines.append(f"  Evidence:    {len(state.evidence)} pieces")
        lines.append("=" * 65)
        lines.append("")

        # Group by tool
        by_tool = {}
        for ev in state.evidence:
            by_tool.setdefault(ev.tool, []).append(ev)

        for tool, events in by_tool.items():
            lines.append(f"[{tool.upper()}]")
            for ev in events:
                lines.append(f"  Confidence: {ev.confidence}")
                for line in ev.result.split("\n"):
                    lines.append(f"    {line}")
            lines.append("")

        lines.append("=" * 65)
        lines.append(f"  End of report. Verdict: {state.verdict}")
        lines.append("=" * 65)

        state.final_report = "\n".join(lines)
        return state


# ============================================================
#                      ORCHESTRATOR
# ============================================================

class Orchestrator:
    """Coordinates specialist agents in sequence."""

    def __init__(self, toolkit):
        self.toolkit = toolkit
        self.agents: List[BaseAgent] = [
            StaticAgent(toolkit),
            SecurityAgent(toolkit),
            CryptoAgent(toolkit),
            ReportAgent(toolkit),
        ]

    def plan(self, state: AnalysisState) -> List[str]:
        """Create an execution plan."""
        plan = []
        for agent in self.agents:
            if agent.can_handle(state):
                plan.append(agent.name)
        return plan

    def run(self, target: str) -> AnalysisState:
        """Run all agents in sequence over the target."""
        state = AnalysisState(target=target)
        state.plan = self.plan(state)

        print(f"\n[Orchestrator] Session: {state.session_id}")
        print(f"[Orchestrator] Target: {target}")
        print(f"[Orchestrator] Plan: {' -> '.join(state.plan)}")
        print()

        for i, agent in enumerate(self.agents, 1):
            print(f"[Step {i}/{len(self.agents)}] {agent.name}: {agent.role}")
            state = agent.act(state)

        return state


# ============================================================
#                         CLI
# ============================================================

def main():
    print("=" * 65)
    print("  NEXUS-RE Multi-Agent System v1.0")
    print("  Phase 4 - LangGraph + ReAct (simulated)")
    print("=" * 65)
    print()

    toolkit = load_toolkit()
    if not toolkit:
        print("[ERROR] Could not load nexus_re_v3.py")
        print("        Make sure it's in the same directory.")
        return

    orchestrator = Orchestrator(toolkit)
    print("Registered agents:")
    for agent in orchestrator.agents:
        print(f"  - {agent.name}: {agent.role}")
    print()

    target = input("Enter file path or hex string (or 'exit'): ").strip()
    if target.lower() == 'exit':
        print("Goodbye!")
        return

    state = orchestrator.run(target)
    print()
    print(state.final_report)


if __name__ == "__main__":
    main()
