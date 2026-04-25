from __future__ import annotations

import json
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
            (root / "src/live.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "generated/user.ts").write_text("export class UserService {}\n", encoding="utf-8")
            (root / "build/user.ts").write_text("export class UserService {}\n", encoding="utf-8")

            report = self.run_find(root, "UserService")
            found = {ref["file"] for ref in report["references"]}

            self.assertEqual(found, {"src/live.ts"})


if __name__ == "__main__":
    unittest.main()
