"""Tests for scraper seniority filter."""
from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "executas" / "job-scraper"))
from scraper_filters import filter_jobs_by_seniority  # noqa: E402


@dataclass
class Job:
    title: str
    description: str = ""


class SeniorityFilterTests(unittest.TestCase):
    def test_senior_only(self) -> None:
        jobs = [Job("Senior Python Dev"), Job("Junior Python Dev")]
        out = filter_jobs_by_seniority(jobs, "senior")
        self.assertEqual(len(out), 1)
        self.assertIn("Senior", out[0].title)

    def test_mid_excludes_senior_and_intern(self) -> None:
        jobs = [
            Job("Senior Python Dev"),
            Job("Python Developer"),
            Job("Software Engineering Intern"),
        ]
        out = filter_jobs_by_seniority(jobs, "mid")
        titles = [j.title for j in out]
        self.assertIn("Python Developer", titles)
        self.assertNotIn("Senior Python Dev", titles)
        self.assertNotIn("Software Engineering Intern", titles)


if __name__ == "__main__":
    unittest.main()
