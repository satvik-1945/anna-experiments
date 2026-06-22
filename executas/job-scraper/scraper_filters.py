"""Job post filters (no heavy scraper deps — safe for unit tests)."""
from __future__ import annotations

from typing import Any

_SENIOR_MARKERS = (
    "senior",
    "sr.",
    "sr ",
    "lead",
    "principal",
    "staff",
    "director",
    "head of",
    "architect",
    "manager",
)
_INTERN_MARKERS = ("intern", "internship", "trainee", "co-op", "co op")
_JUNIOR_MARKERS = (
    "junior",
    "jr.",
    "jr ",
    "entry level",
    "entry-level",
    "graduate",
    "fresher",
    "associate",
)


def _job_blob(job: Any) -> str:
    return f"{job.title} {getattr(job, 'description', '')}".lower()


def _has_any(blob: str, markers: tuple[str, ...]) -> bool:
    return any(m in blob for m in markers)


def filter_jobs_by_seniority(jobs: list[Any], seniority: str | None) -> list[Any]:
    level = (seniority or "any").strip().lower()
    if level in ("", "any", "all"):
        return jobs

    out: list[Any] = []
    for job in jobs:
        blob = _job_blob(job)
        is_intern = _has_any(blob, _INTERN_MARKERS)
        is_junior = _has_any(blob, _JUNIOR_MARKERS)
        is_senior = _has_any(blob, _SENIOR_MARKERS)

        if level == "intern":
            if is_intern:
                out.append(job)
        elif level == "junior":
            if is_junior and not is_senior:
                out.append(job)
            elif not is_intern and not is_senior and not is_junior:
                out.append(job)
        elif level == "mid":
            if not is_intern and not is_senior:
                out.append(job)
        elif level == "senior":
            if is_senior:
                out.append(job)
        else:
            out.append(job)
    return out
