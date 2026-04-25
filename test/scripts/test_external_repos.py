from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "skills/p2d/benchmarks/repos.json"
SKILL = REPO_ROOT / "skills/p2d/SKILL.md"
METADATA = REPO_ROOT / "skills/p2d/metadata.json"
SECTIONS = REPO_ROOT / "skills/p2d/rules/_sections.md"
RULES_DIR = REPO_ROOT / "skills/p2d/rules"


class ExternalReposConfigTests(unittest.TestCase):
    def test_config_shape_and_pins(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(config["repos"]), 6)
        for repo in config["repos"]:
            with self.subTest(repo=repo["id"]):
                self.assertRegex(repo["commit"], r"^[0-9a-f]{40}$")
                self.assertTrue(repo["targets"])
                for target in repo["targets"]:
                    self.assertTrue(target["symbol"])
                    self.assertTrue(target["expected_files"])
                    self.assertTrue(target["task_type"])
                    self.assertTrue(target["language"])
                    self.assertTrue(target["notes"])
                    for file in target["expected_files"]:
                        self.assertFalse(file.startswith("/"))
                        self.assertNotIn("..", Path(file).parts)

    def test_metadata_version_and_rule_sections_are_consistent(self) -> None:
        skill_text = SKILL.read_text(encoding="utf-8")
        metadata = json.loads(METADATA.read_text(encoding="utf-8"))
        version_match = re.search(r"version:\s*'([^']+)'", skill_text)

        self.assertIsNotNone(version_match)
        self.assertEqual(version_match.group(1), metadata["version"])

        sections = SECTIONS.read_text(encoding="utf-8")
        for rule in RULES_DIR.glob("*.md"):
            if rule.name == "_sections.md":
                continue
            with self.subTest(rule=rule.name):
                self.assertIn(f"({rule.stem})", sections)


if __name__ == "__main__":
    unittest.main()
