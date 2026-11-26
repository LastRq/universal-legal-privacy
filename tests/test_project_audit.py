import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ProjectAuditTests(unittest.TestCase):
    def run_audit(self, root, *args):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/project_audit.py"),
                                 "--project", str(root), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_hybrid_vault_no_values_or_private_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tauri.conf.json").write_text('{"secret":"manifest-private-marker"}')
            (root / "AndroidManifest.xml").write_text("<manifest/>")
            (root / "app.rs").write_text("let totp = \"private-value\"; // Argon2\n")
            (root / "vaults").mkdir()
            (root / "vaults" / "real.py").write_text("apiKey = 'never-inspect'")
            (root / ".env").write_text("SECRET=hidden")
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            report = self.run_audit(root)
            self.assertEqual(report["status"], "manual-review-required")
            self.assertEqual({x["platform"] for x in report["platform_candidates"]}, {"desktop", "android"})
            self.assertIn("encryption", report["candidate_modules"]["capabilities"])
            self.assertNotIn("private-value", json.dumps(report))
            self.assertNotIn("manifest-private-marker", json.dumps(report))
            self.assertNotIn("real.py", json.dumps(report))
            self.assertEqual(before, sorted(str(p.relative_to(root)) for p in root.rglob("*")))

    def test_unknown_project_no_false_compliance(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.run_audit(td)
            self.assertEqual(report["status"], "manual-review-required")
            self.assertEqual(report["platform_candidates"], [])
            self.assertEqual(report["candidate_modules"], {"capabilities": []})

    def test_file_limit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("a.py", "b.py"):
                (root / name).write_text("print('hello')")
            report = self.run_audit(root, "--max-files", "1")
            self.assertTrue(report["truncated"])
            self.assertEqual(report["source_files_attempted"], 1)


if __name__ == "__main__":
    unittest.main()
