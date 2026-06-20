"""Tests for resume-composer."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_TEX = ROOT / "tests" / "fixtures" / "resume_base.tex"
FIXTURE_RSECTION = ROOT / "tests" / "fixtures" / "resume_rsection.tex"

import sys

sys.path.insert(0, str(ROOT / "executas" / "resume-composer"))
from composer_core import compose_for_job, find_skills_block, replace_skills_section  # noqa: E402


class ResumeComposerTests(unittest.TestCase):
    def test_tailors_skills_section(self) -> None:
        base = FIXTURE_TEX.read_text(encoding="utf-8")
        entry = {
            "job": {
                "title": "Senior Python Developer",
                "company": "Tech Co",
                "description": "Python FastAPI Docker Kubernetes AWS required.",
            },
            "matched_skills": ["python", "fastapi", "docker", "aws"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RESUMATCH_RESUMES_DIR"] = tmp
            result = compose_for_job(entry, base_tex=base)
            out = Path(result["output_path"]).read_text(encoding="utf-8")
            self.assertIn("Role-Aligned Highlights", out)
            self.assertIn("Python", out)
            self.assertNotIn("Kubernetes", out)  # not in original resume — no fabrication
            self.assertIn("\\section{Education}", out)

    def test_replace_skills_preserves_rest(self) -> None:
        base = FIXTURE_TEX.read_text(encoding="utf-8")
        new = "\\section{Skills}\n\\begin{itemize}\n\\item Test.\n\\end{itemize}\n\n"
        patched = replace_skills_section(base, new)
        self.assertIn("\\section{Work Experience}", patched)
        self.assertIn("\\item Test.", patched)

    def test_rsection_tabular_resume(self) -> None:
        base = FIXTURE_RSECTION.read_text(encoding="utf-8")
        self.assertIsNotNone(find_skills_block(base))
        entry = {
            "job": {
                "title": "Python Backend Engineer",
                "company": "Startup",
                "description": "Python FastAPI Docker AWS required.",
            },
            "matched_skills": ["python", "fastapi", "docker", "aws"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RESUMATCH_RESUMES_DIR"] = tmp
            result = compose_for_job(entry, base_tex=base)
            out = Path(result["output_path"]).read_text(encoding="utf-8")
            self.assertEqual(result["skills_format"], "rsection")
            self.assertIn("Role-Aligned", out)
            self.assertIn("\\begin{rSection}{Technical Skills}", out)
            self.assertIn("FastAPI", out)
            self.assertIn("\\begin{rSection}{Work Experience}", out)

    def test_compile_pdf_mock(self) -> None:
        from unittest.mock import patch

        from composer_core import compile_pdf

        base = FIXTURE_RSECTION.read_text(encoding="utf-8")
        entry = {
            "job": {"title": "Engineer", "company": "Acme", "description": "Python"},
            "matched_skills": ["python"],
        }
        fake_pdf = b"%PDF-1.4 fake"
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RESUMATCH_RESUMES_DIR"] = tmp
            os.environ["RESUMATCH_PDF_DIR"] = tmp
            compose_for_job(entry, base_tex=base)
            tex_path = Path(tmp) / "resume_engineer_acme.tex"
            with patch("composer_core._find_tectonic", return_value="/bin/tectonic"), patch(
                "composer_core.subprocess.run",
            ) as mock_run:
                mock_run.return_value.returncode = 0
                pdf_path = tex_path.with_suffix(".pdf")
                pdf_path.write_bytes(fake_pdf)
                result = compile_pdf(tex_path=str(tex_path))
            self.assertTrue(result["pdf_filename"].endswith(".pdf"))
            self.assertEqual(result["size_bytes"], len(fake_pdf))
            self.assertIn("pdf_base64", result)


if __name__ == "__main__":
    unittest.main()
