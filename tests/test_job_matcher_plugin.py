"""Tests for job-matcher executa."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "executas" / "job-matcher"
PLUGIN = PLUGIN_DIR / "job_matcher_plugin.py"

PROFILE = {
    "schema_version": 1,
    "profile": {
        "domain": "software_engineering",
        "seniority": "mid",
        "years_experience": 3,
        "location": "India",
        "resume_text": "Python FastAPI Docker React software engineer 3 years",
        "skills": ["python", "fastapi", "docker", "react"],
    },
}

JOBS = {
    "jobs": [
        {
            "title": "Senior Python Developer",
            "company": "Tech Co",
            "description": "Python FastAPI Docker Kubernetes required.",
            "apply_url": "https://example.com/1",
        },
        {
            "title": "Accountant",
            "company": "Finance Co",
            "description": "GST audit tally accounting only.",
            "apply_url": "https://example.com/2",
        },
    ]
}


def rpc(payload: dict, env: dict) -> dict:
    proc = subprocess.run(
        ["uv", "run", "job-matcher"],
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout.strip().splitlines()[-1])


class JobMatcherTests(unittest.TestCase):
    def test_score_ranks_python_job_higher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile_path = Path(tmp) / "profile.json"
            jobs_path = Path(tmp) / "jobs.json"
            profile_path.write_text(json.dumps(PROFILE), encoding="utf-8")
            jobs_path.write_text(json.dumps(JOBS), encoding="utf-8")
            env = os.environ.copy()
            env["RESUMATCH_PROFILE_PATH"] = str(profile_path)
            env["RESUMATCH_JOBS_PATH"] = str(jobs_path)
            env["RESUMATCH_MATCH_PATH"] = str(Path(tmp) / "match.json")

            out = rpc(
                {
                    "jsonrpc": "2.0",
                    "method": "invoke",
                    "id": 1,
                    "params": {
                        "tool": "job_matcher",
                        "arguments": {"action": "score", "threshold": 50},
                    },
                },
                env=env,
            )
            self.assertTrue(out["result"]["success"])
            results = out["result"]["data"]["results"]
            self.assertGreater(results[0]["score"], results[1]["score"])
            self.assertEqual(results[0]["job"]["title"], "Senior Python Developer")


if __name__ == "__main__":
    unittest.main()
