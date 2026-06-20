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
            match = {
                "passed": [
                    {
                        "score": 85,
                        "matched_skills": ["python"],
                        "job": {
                            "title": "Python Dev",
                            "company": "Co",
                            "apply_url": "https://example.com/job/1",
                            "location": "India",
                            "source": "indeed",
                        },
                    }
                ]
            }
            manifest = {
                "resumes": [
                    {
                        "job_title": "Python Dev",
                        "company": "Co",
                        "apply_url": "https://example.com/job/1",
                        "output_path": str(tmp_path / "resume_python_dev_co.tex"),
                    }
                ]
            }
            (tmp_path / "resume_python_dev_co.tex").write_text("% tex")
            os.environ["RESUMATCH_MATCH_PATH"] = str(tmp_path / "match.json")
            os.environ["RESUMATCH_RESUMES_MANIFEST"] = str(tmp_path / "manifest.json")
            os.environ["RESUMATCH_PACKS_PATH"] = str(tmp_path / "packs.json")
            (tmp_path / "match.json").write_text(json.dumps(match))
            (tmp_path / "manifest.json").write_text(json.dumps(manifest))

            result = prepare_all()
            self.assertEqual(result["count"], 1)
            pack = result["packs"][0]
            self.assertEqual(pack["apply_url"], "https://example.com/job/1")
            self.assertIn("Overleaf", pack["checklist"][1])
            self.assertNotIn("email", " ".join(pack["checklist"]).lower())


if __name__ == "__main__":
    unittest.main()
