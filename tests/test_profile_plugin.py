"""Tests for resumatch-profile executa."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "executas" / "profile"
PLUGIN = PLUGIN_DIR / "profile_plugin.py"

SAMPLE_RESUME = """
Satvik Tejas
tejas@example.com
+91 98765 43210

Software engineer with 3 years experience in Python, FastAPI, Docker, and React.
"""


def rpc(payload: dict, env: dict | None = None) -> dict:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        [sys.executable, str(PLUGIN)],
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
        env=merged,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout.strip().splitlines()[-1])


class ProfilePluginTests(unittest.TestCase):
    def test_describe(self) -> None:
        out = rpc({"jsonrpc": "2.0", "method": "describe", "id": 1})
        self.assertEqual(out["result"]["name"], "resumatch-profile")
        tools = [t["name"] for t in out["result"]["tools"]]
        self.assertIn("user_profile", tools)

    def test_save_and_get(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile_path = Path(tmp) / "profile.json"
            env = {"RESUMATCH_PROFILE_PATH": str(profile_path)}
            save = rpc(
                {
                    "jsonrpc": "2.0",
                    "method": "invoke",
                    "id": 2,
                    "params": {
                        "tool": "user_profile",
                        "arguments": {
                            "action": "save",
                            "domain": "software_engineering",
                            "seniority": "mid",
                            "years_experience": 3,
                            "location": "India",
                            "resume_text": SAMPLE_RESUME,
                        },
                    },
                },
                env=env,
            )
            self.assertTrue(save["result"]["success"])
            self.assertIn("python", save["result"]["data"]["skills"])
            term = save["result"]["data"]["effective_search_term"]
            self.assertIn("python", term.lower())
            self.assertIn("engineer", term.lower())

            got = rpc(
                {
                    "jsonrpc": "2.0",
                    "method": "invoke",
                    "id": 3,
                    "params": {"tool": "user_profile", "arguments": {"action": "get"}},
                },
                env=env,
            )
            self.assertTrue(got["result"]["data"]["exists"])
            self.assertEqual(got["result"]["data"]["domain"], "software_engineering")


if __name__ == "__main__":
    unittest.main()
