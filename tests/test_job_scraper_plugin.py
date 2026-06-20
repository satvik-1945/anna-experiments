"""Tests for the job scraper Executa plugin."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "executas" / "job-scraper"
PLUGIN = PLUGIN_DIR / "job_scraper_plugin.py"


def _run_plugin(request: dict) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PLUGIN_DIR)
    proc = subprocess.run(
        [sys.executable, str(PLUGIN)],
        input=json.dumps(request) + "\n",
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return json.loads(proc.stdout.strip())


class JobScraperPluginTests(unittest.TestCase):
    def test_describe(self) -> None:
        out = _run_plugin({"jsonrpc": "2.0", "method": "describe", "id": 1})
        self.assertEqual(out["result"]["name"], "job-scraper")
        tools = [t["name"] for t in out["result"]["tools"]]
        self.assertIn("job_scraper", tools)

    def test_summary_before_scrape(self) -> None:
        out = _run_plugin(
            {
                "jsonrpc": "2.0",
                "method": "invoke",
                "id": 2,
                "params": {
                    "tool": "job_scraper",
                    "arguments": {"action": "summary"},
                },
            }
        )
        self.assertTrue(out["result"]["success"])
        self.assertEqual(out["result"]["data"]["count"], 0)

    @patch.dict(os.environ, {"RESUMATCH_SMOKE_MOCK": "1"}, clear=False)
    def test_scrape_mocked(self) -> None:
        out = _run_plugin(
            {
                "jsonrpc": "2.0",
                "method": "invoke",
                "id": 3,
                "params": {
                    "tool": "job_scraper",
                    "arguments": {
                        "action": "scrape",
                        "mode": "free",
                        "results_wanted": 5,
                        "hours_old": 24,
                        "description_max_chars": 50,
                    },
                },
            }
        )
        self.assertTrue(out["result"]["success"])
        data = out["result"]["data"]
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["jobs"][0]["title"], "Mock Software Engineer")
        self.assertTrue(data["jobs"][0]["description"].endswith("…"))


if __name__ == "__main__":
    unittest.main()
