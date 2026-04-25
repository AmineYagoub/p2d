from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/p2d/scripts/p2d-state-map"


class StateMapTests(unittest.TestCase):
    def run_state(self, root: Path, *terms: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *terms, "--root", str(root), "--json"],
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_maps_synonyms_and_files_outside_naming_conventions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "src/session.tsx": 'export const AuthContext = createContext({ userId: null, token: null });\n',
                "src/profile-data.ts": 'export const useAccountStore = create(() => ({ userId: null, displayName: null }));\n',
                "src/billing.ts": 'export const useBillingStore = create(() => ({ invoiceId: null }));\n',
            }
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            report = self.run_state(root, "user", "account")
            found = {owner["file"] for owner in report["owners"]}

            self.assertEqual(found, {"src/session.tsx", "src/profile-data.ts"})
            self.assertTrue(report["potential_split_brain"])
            self.assertEqual(report["unknown_terms"], [])
            self.assertTrue(any(owner["overlapping_fields"] for owner in report["owners"]))

    def test_supports_terms_option_and_unknown_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src/auth.ts").write_text(
                'export const AuthContext = createContext({ token: null });\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--terms", "token", "cart", "--root", str(root), "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            report = json.loads(result.stdout)

            self.assertEqual({owner["file"] for owner in report["owners"]}, {"src/auth.ts"})
            self.assertEqual(report["unknown_terms"], ["cart"])


if __name__ == "__main__":
    unittest.main()
