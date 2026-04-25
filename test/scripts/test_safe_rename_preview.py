from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/p2d/scripts/p2d-safe-rename-preview"


class SafeRenamePreviewTests(unittest.TestCase):
    def test_reports_buckets_without_mutating_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            target = root / "src/user.ts"
            original = (
                "export class UserService {}\n"
                "const token = 'UserService';\n"
                "new UserService();\n"
            )
            target.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "UserService",
                    "AccountService",
                    "--root",
                    str(root),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            report = json.loads(result.stdout)

            self.assertEqual(target.read_text(encoding="utf-8"), original)
            self.assertEqual(report["total_matches"], 3)
            self.assertGreaterEqual(report["categories"].get("definition", 0), 1)
            self.assertGreaterEqual(report["categories"].get("string", 0), 1)
            self.assertIn("string", report["requires_review"])


if __name__ == "__main__":
    unittest.main()
