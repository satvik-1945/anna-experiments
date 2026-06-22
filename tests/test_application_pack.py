"""Tests for application-pack."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys_path = ROOT / "executas" / "application-pack"
import sys

sys.path.insert(0, str(sys_path))
from pack_core import prepare_all  # noqa: E402


class ApplicationPackTests(unittest.TestCase):
    def test_prepare_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            jobs = {
                "count": 1,
                "jobs": [
                    {
                        "title": "Python Dev",
                        "company": "Co",
                        "apply_url": "https://example.com/job/1",
                        "location": "India",
                        "source": "indeed",
                    }
                ],
            }
            manifest = {
                "resumes": [
                    {
                        "job_title": "Python Dev",
                        "company": "Co",
                        "apply_url": "https://example.com/job/1",
                        "output_path": str(tmp_path / "resume_python_dev_co.tex"),
                        "matched_skills_used": ["python", "fastapi"],
                    }
                ]
            }
            (tmp_path / "resume_python_dev_co.tex").write_text("% tex")
            profile_path = tmp_path / "profile.json"
            profile_path.write_text(json.dumps({"target_skills": ["python", "fastapi", "docker", "aws"]}))
            os.environ["RESUMATCH_PROFILE_PATH"] = str(profile_path)
            os.environ["RESUMATCH_JOBS_PATH"] = str(tmp_path / "jobs.json")
            os.environ["RESUMATCH_RESUMES_MANIFEST"] = str(tmp_path / "manifest.json")
            os.environ["RESUMATCH_PACKS_PATH"] = str(tmp_path / "packs.json")
            (tmp_path / "jobs.json").write_text(json.dumps(jobs))
            (tmp_path / "manifest.json").write_text(json.dumps(manifest))

            result = prepare_all()
            self.assertEqual(result["count"], 1)
            packs_path = tmp_path / "packs.json"
            saved = json.loads(packs_path.read_text(encoding="utf-8"))
            pack = saved["packs"][0]
            self.assertEqual(pack["apply_url"], "https://example.com/job/1")
            self.assertIn("Overleaf", pack["checklist"][1])
            self.assertNotIn("email", " ".join(pack["checklist"]).lower())
            # 2 matched of 4 target skills -> 50% (persisted on disk for future use)
            self.assertEqual(pack["match_pct"], 50)
            self.assertEqual(len(result["packs"]), 1)
            self.assertNotIn("checklist", result["packs"][0])
            # slim preview stays minimal (no heavy fields) so large pack counts fit RPC
            self.assertNotIn("matched_skills", result["packs"][0])
            os.environ.pop("RESUMATCH_PROFILE_PATH", None)

    def test_list_paginates(self) -> None:
        from pack_core import list_packs

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            packs = [
                {"job_index": i, "job_title": f"Job {i}", "company": "Co",
                 "apply_url": f"https://example.com/job/{i}", "source": "indeed"}
                for i in range(120)
            ]
            packs_path = tmp_path / "packs.json"
            packs_path.write_text(json.dumps({"count": len(packs), "packs": packs}))
            os.environ["RESUMATCH_PACKS_PATH"] = str(packs_path)

            page1 = list_packs(offset=0, limit=50)
            self.assertEqual(page1["total"], 120)
            self.assertEqual(len(page1["packs"]), 50)
            self.assertTrue(page1["has_more"])

            page3 = list_packs(offset=100, limit=50)
            self.assertEqual(len(page3["packs"]), 20)
            self.assertFalse(page3["has_more"])
            os.environ.pop("RESUMATCH_PACKS_PATH", None)


if __name__ == "__main__":
    unittest.main()
