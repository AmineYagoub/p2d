from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/p2d/scripts/p2d-benchmark"


class BenchmarkTests(unittest.TestCase):
    def run_benchmark(self, root: Path, expected: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "UserService", "--root", str(root), "--expected", str(expected), "--json", *extra],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_succeeds_with_complete_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            expected = root / "expected.json"
            expected.write_text(json.dumps({"files": ["src/user.ts"]}), encoding="utf-8")

            result = self.run_benchmark(root, expected)
            report = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["recall_percent"], 100.0)
            self.assertEqual(report["precision_percent"], 100.0)

    def test_fails_when_expected_file_is_missed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "src/auth.ts").write_text("export class AuthService {}\n", encoding="utf-8")
            expected = root / "expected.json"
            expected.write_text(json.dumps({"files": ["src/user.ts", "src/auth.ts"]}), encoding="utf-8")

            result = self.run_benchmark(root, expected)
            report = json.loads(result.stdout)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report["false_negative_files"], ["src/auth.ts"])
            self.assertTrue(report["failed_thresholds"])

    def test_reports_false_positives_and_precision_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "src/extra.ts").write_text("console.log(UserService)\n", encoding="utf-8")
            expected = root / "expected.json"
            expected.write_text(json.dumps({"files": ["src/user.ts"]}), encoding="utf-8")

            result = self.run_benchmark(root, expected, "--fail-under-precision", "100")
            report = json.loads(result.stdout)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report["false_positive_files"], ["src/extra.ts"])
            self.assertIn("precision", report["failed_thresholds"][0])


if __name__ == "__main__":
    unittest.main()
