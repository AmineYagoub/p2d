from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/p2d/scripts/p2d-deletion-sim"


class DeletionSimTests(unittest.TestCase):
    def run_sim(self, root: Path, module: str = "./feature") -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), module, "--root", str(root), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
        return json.loads(result.stdout)

    def test_classifies_language_and_framework_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "src/static.ts": 'import { runFeature } from "./feature";\n',
                "src/type.ts": 'import type { FeatureConfig } from "./feature";\n',
                "src/index.ts": 'export { runFeature } from "./feature";\n',
                "src/lazy.ts": 'const feature = import("./feature");\n',
                "src/commonjs.js": 'const feature = require("./feature");\n',
                "src/routes.ts": 'router.get("./feature", handler);\n',
                "src/app.module.ts": 'providers: ["./feature"]\n',
                "package.json": '{"exports": {"./feature": "./src/feature.ts"}}\n',
                "config.yaml": 'featureModule: "./feature"\n',
                "src/feature.spec.ts": 'expect("./feature").toBeTruthy();\n',
            }
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            report = self.run_sim(root)
            buckets = report["buckets"]

            for bucket in {
                "static-import",
                "type-only",
                "re-export",
                "dynamic-import",
                "commonjs",
                "route-registration",
                "di-container",
                "package-export",
                "config-reference",
                "test",
            }:
                self.assertGreaterEqual(buckets.get(bucket, 0), 1, bucket)
            self.assertEqual(report["type_only_cleanup_candidates"], 1)
            self.assertFalse(report["safe_to_delete"])


if __name__ == "__main__":
    unittest.main()
