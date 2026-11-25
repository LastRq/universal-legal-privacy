"""Tests for catalog integrity and conservative module composition."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("module_plan", ROOT / "scripts/module_plan.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


class ModuleTests(unittest.TestCase):
    def test_catalog(self):
        groups = planner.load_catalog()
        self.assertEqual({k: len(v) for k, v in groups.items()},
                         {"sectors": 40, "models": 24, "capabilities": 35})

    def test_hybrid(self):
        result = planner.plan(
            {"sectors": ["healthcare", "technology"], "models": ["saas", "multitenant"],
             "capabilities": ["sensitive-data", "sensitive-data", "authentication"]},
            ["EC", "EC"], {"capabilities": ["biometrics", "authentication"]})
        self.assertEqual(len(result["modules"]), 6)
        self.assertEqual([x["id"] for x in result["candidate_modules"]], ["biometrics"])
        self.assertEqual(result["jurisdictions_to_verify"], ["EC"])
        self.assertEqual(result["status"], "research-required")

    def test_unknown(self):
        with self.assertRaises(ValueError):
            planner.plan({"sectors": ["invented"]})
        with self.assertRaises(ValueError):
            planner.plan({}, candidates={"other": ["invalid"]})

    def test_empty_fails_closed(self):
        result = planner.plan({})
        self.assertEqual(result["modules"], [])
        self.assertIn("Confirm applicable jurisdictions", result["blockers"])
        self.assertIn("Verify official legal sources and applicability", result["blockers"])


if __name__ == "__main__":
    unittest.main()
