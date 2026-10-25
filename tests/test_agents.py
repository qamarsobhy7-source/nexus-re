"""
NEXUS-RE Agents Test Suite
Tests the multi-agent orchestrator (Static, Security, Crypto, Report).
"""
import importlib.util
import os
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TEST_DIR)


def find_file(name):
    candidates = [
        os.path.join(REPO_ROOT, name),
        os.path.join(REPO_ROOT, "src", "agents", name),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def load_module(name, path):
    if not path:
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


toolkit = load_module("nexus_re_v3", find_file("nexus_re_v3.py"))
agents_mod = load_module("nexus_agents", find_file("nexus_agents.py"))


@unittest.skipIf(agents_mod is None or toolkit is None, "Agents or Toolkit not found")
class TestAgents(unittest.TestCase):
    """Tests for multi-agent orchestration."""

    def test_orchestrator_init(self):
        """Orchestrator can be instantiated with the toolkit."""
        orch = agents_mod.Orchestrator(toolkit)
        self.assertIsNotNone(orch)
        self.assertEqual(len(orch.agents), 4)

    def test_orchestrator_has_agents(self):
        """Orchestrator registers 4 agents: Static, Security, Crypto, Report."""
        orch = agents_mod.Orchestrator(toolkit)
        names = [a.name for a in orch.agents]
        self.assertIn("static", names)
        self.assertIn("security", names)
        self.assertIn("crypto", names)
        self.assertIn("report", names)

    def test_plan_generation(self):
        """Plan returns a list of agent names."""
        orch = agents_mod.Orchestrator(toolkit)
        state = agents_mod.AnalysisState(target="7f454c4602010100")
        plan = orch.plan(state)
        self.assertIsInstance(plan, list)
        self.assertGreater(len(plan), 0)

    def test_full_run(self):
        """Full orchestrator run returns state with evidence."""
        orch = agents_mod.Orchestrator(toolkit)
        state = orch.run("7f454c4602010100000000000000000048656c6c6f204e455855532d5245")
        self.assertIsNotNone(state)
        self.assertGreater(len(state.evidence), 0)
        self.assertIsNotNone(state.session_id)
        self.assertIn(state.verdict, ["UNKNOWN", "MALICIOUS", "SUSPICIOUS", "CLEAN"])

    def test_evidence_structure(self):
        """Each evidence item has required fields."""
        orch = agents_mod.Orchestrator(toolkit)
        state = orch.run("7f454c4602010100")
        for ev in state.evidence:
            self.assertIsNotNone(ev.tool)
            self.assertIsNotNone(ev.result)
            self.assertIn(ev.confidence, ["HIGH", "MEDIUM", "LOW"])

    def test_report_generated(self):
        """Report agent produces a final report."""
        orch = agents_mod.Orchestrator(toolkit)
        state = orch.run("7f454c46")
        self.assertTrue(len(state.final_report) > 0)
        self.assertIn("NEXUS-RE", state.final_report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
