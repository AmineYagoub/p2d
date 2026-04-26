from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/p2d/scripts/p2d-find-symbol"


class FindSymbolTests(unittest.TestCase):
    def run_find(self, root: Path, symbol: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), symbol, "--root", str(root), "--json"],
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_finds_symbol_across_supported_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "src/service.ts": "export class BillingService {}\n",
                "src/service.py": "class BillingService:\n    pass\n",
                "src/service.go": "type BillingService struct{}\n",
                "src/service.rs": "pub struct BillingService {}\n",
                "src/Service.java": "class BillingService {}\n",
            }
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            report = self.run_find(root, "BillingService")
            found = {ref["file"] for ref in report["references"]}

            self.assertEqual(found, set(files))
            self.assertGreaterEqual(report["categories"].get("definition", 0), 5)

    def test_ignores_generated_and_build_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "generated").mkdir()
            (root / "build").mkdir()
            (root / ".p2d-bench/repos/example").mkdir(parents=True)
            (root / ".code-review-graph").mkdir()
            (root / "src/live.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "generated/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "build/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / ".p2d-bench/repos/example/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / ".code-review-graph/user.ts").write_text("export class UserService {}\n", encoding="utf-8")

            report = self.run_find(root, "UserService")
            found = {ref["file"] for ref in report["references"]}

            self.assertEqual(found, {"src/live.ts"})

    def test_filters_directories_and_extensions_case_insensitively(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "Node_Modules").mkdir()
            (root / "DIST").mkdir()
            (root / "src/live.PY").write_text("class UserService:\n    pass\n", encoding="utf-8")
            (root / "Node_Modules/ignored.py").write_text("class UserService:\n    pass\n", encoding="utf-8")
            (root / "DIST/ignored.py").write_text("class UserService:\n    pass\n", encoding="utf-8")

            report = self.run_find(root, "UserService")
            found = {ref["file"] for ref in report["references"]}

            self.assertEqual(found, {"src/live.PY"})

    @unittest.skipIf(os.geteuid() == 0, "root can read permission-restricted files")
    def test_unreadable_file_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            unreadable = root / "src/blocked.py"
            unreadable.write_text("class UserService:\n    pass\n", encoding="utf-8")
            unreadable.chmod(0)
            try:
                report = self.run_find(root, "UserService")
            finally:
                unreadable.chmod(0o644)

            self.assertEqual(report["total"], 0)


if __name__ == "__main__":
    unittest.main()
