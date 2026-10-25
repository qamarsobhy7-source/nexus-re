"""
NEXUS-RE API Test Suite
Tests the REST API endpoints without requiring a running server.
"""
import importlib.util
import os
import unittest
import sys

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TEST_DIR)


def find_api_module():
    candidates = [
        os.path.join(REPO_ROOT, "api_render.py"),
        os.path.join(REPO_ROOT, "src", "api", "api.py"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def load_api():
    path = find_api_module()
    if not path:
        return None
    # Set dev mode to avoid auth blocking during tests
    os.environ["NEXUS_DEV_MODE"] = "true"
    spec = importlib.util.spec_from_file_location("api_module", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


api_mod = load_api()


@unittest.skipIf(api_mod is None, "API module not found")
class TestAPIStructure(unittest.TestCase):
    """Tests for API structure and handler."""

    def test_handler_class_exists(self):
        """NexusAPIHandler class exists."""
        self.assertTrue(hasattr(api_mod, "NexusAPIHandler"))

    def test_run_server_function_exists(self):
        """run_server function exists."""
        self.assertTrue(hasattr(api_mod, "run_server"))

    def test_handler_has_check_auth(self):
        """Handler has _check_auth method."""
        handler = api_mod.NexusAPIHandler
        self.assertTrue(hasattr(handler, "_check_auth"))

    def test_handler_has_get_post(self):
        """Handler has do_GET and do_POST methods."""
        handler = api_mod.NexusAPIHandler
        self.assertTrue(hasattr(handler, "do_GET"))
        self.assertTrue(hasattr(handler, "do_POST"))

    def test_handler_has_options(self):
        """Handler has do_OPTIONS for CORS preflight."""
        handler = api_mod.NexusAPIHandler
        self.assertTrue(hasattr(handler, "do_OPTIONS"))

    def test_send_json_method(self):
        """Handler has _send_json helper."""
        handler = api_mod.NexusAPIHandler
        self.assertTrue(hasattr(handler, "_send_json"))

    def test_toolkit_loaded(self):
        """API module successfully loads the toolkit."""
        self.assertIsNotNone(api_mod.toolkit)

    def test_agents_loaded(self):
        """API module successfully loads agents."""
        self.assertIsNotNone(api_mod.agents_mod)


if __name__ == "__main__":
    unittest.main(verbosity=2)
