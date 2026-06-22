"""Build manual-apply packs: job link + tailored resume path. No email draft."""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESUMATCH_DIR = Path.home() / ".anna" / "resumatch"
DEFAULT_JOBS_PATH = RESUMATCH_DIR / "jobs_latest.json"
DEFAULT_RESUMES_DIR = RESUMATCH_DIR / "resumes"
DEFAULT_MANIFEST_PATH = DEFAULT_RESUMES_DIR / "manifest.json"
DEFAULT_PACKS_PATH = RESUMATCH_DIR / "application_packs.json"
DEFAULT_PROFILE_PATH = RESUMATCH_DIR / "profile.json"


def _path(env_key: str, default: Path) -> Path:
    override = os.environ.get(env_key, "").strip()
    return Path(override) if override else default


def _target_skill_count() -> int:
    profile_path = _path("RESUMATCH_PROFILE_PATH", DEFAULT_PROFILE_PATH)
    if not profile_path.exists():
        return 0
    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
        data = raw.get("profile") or raw
        skills = data.get("target_skills") or []
        return len(skills) if isinstance(skills, list) else 0
    except (json.JSONDecodeError, OSError):
        return 0


def _match_pct(matched: Any, target_count: int) -> int:
    n = len(matched) if isinstance(matched, list) else 0
    if target_count <= 0:
        return 50 if n else 0
    return max(0, min(100, round(100 * n / target_count)))


def _load_scraped_jobs() -> list[dict[str, Any]]:
    jobs_path = _path("RESUMATCH_JOBS_PATH", DEFAULT_JOBS_PATH)
    if not jobs_path.exists():
        raise ValueError("No jobs_latest.json — run job_scraper action scrape first.")
    raw = json.loads(jobs_path.read_text(encoding="utf-8"))
    jobs = list(raw.get("jobs") or [])
    if not jobs:
        raise ValueError("No scraped jobs. Run job_scraper scrape first.")
    return [{"job": job} for job in jobs]


def _load_composed() -> list[dict[str, Any]]:
    manifest = _path("RESUMATCH_RESUMES_MANIFEST", DEFAULT_MANIFEST_PATH)
    if not manifest.exists():
        raise ValueError("No composed resumes — run resume_composer action compose_all first.")
    raw = json.loads(manifest.read_text(encoding="utf-8"))
    resumes = raw.get("resumes") or []
    if not resumes:
        raise ValueError("Resume manifest is empty.")
    return resumes


def _checklist(apply_url: str, resume_path: str) -> list[str]:
    return [
        f"Open job posting: {apply_url}",
        f"Compile tailored resume in Overleaf: {resume_path}",
        "Download PDF and review — confirm Skills section is accurate.",
        "Apply manually on the job site (Indeed / company portal). You click Submit.",
    ]


def build_pack(
    job_index: int,
    job_entry: dict[str, Any],
    composed: dict[str, Any],
    target_skill_count: int = 0,
) -> dict[str, Any]:
    job = job_entry.get("job") or job_entry
    matched = composed.get("matched_skills_used") or []
    return {
        "job_index": job_index,
        "job_title": job.get("title") or composed.get("job_title"),
        "company": job.get("company") or composed.get("company"),
        "apply_url": job.get("apply_url") or composed.get("apply_url"),
        "location": job.get("location", ""),
        "source": job.get("source", ""),
        "published_at": job.get("published_at") or job.get("date_posted") or "",
        "resume_tex_path": composed.get("output_path"),
        "matched_skills": matched,
        "match_pct": _match_pct(matched, target_skill_count),
        "checklist": _checklist(
            str(job.get("apply_url") or composed.get("apply_url") or ""),
            str(composed.get("output_path") or ""),
        ),
    }


def _slim_pack(p: dict[str, Any]) -> dict[str, Any]:
    """Minimal fields the listing table needs. Kept tiny so large pack counts
    never exceed the host RPC payload limit (Preview PDF resolves by job_index)."""
    return {
        "job_index": p.get("job_index"),
        "job_title": p.get("job_title"),
        "company": p.get("company"),
        "apply_url": p.get("apply_url"),
        "location": p.get("location", ""),
        "source": p.get("source"),
        "published_at": p.get("published_at", ""),
    }


def prepare_all(*, max_response_packs: int = 5) -> dict[str, Any]:
    scraped = _load_scraped_jobs()
    composed_list = _load_composed()
    if len(composed_list) < len(scraped):
        raise ValueError(
            f"Only {len(composed_list)} composed resumes for {len(scraped)} scraped jobs. "
            "Run resume_composer compose_all."
        )

    target_count = _target_skill_count()
    packs = [
        build_pack(i, scraped[i], composed_list[i], target_count)
        for i in range(len(scraped))
    ]
    payload = {
        "prepared_at": datetime.now(UTC).isoformat(),
        "count": len(packs),
        "packs": packs,
    }
    out = _path("RESUMATCH_PACKS_PATH", DEFAULT_PACKS_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    preview = [_slim_pack(p) for p in packs[: max(0, max_response_packs)]]
    return {
        "prepared_at": payload["prepared_at"],
        "count": len(packs),
        "saved_to": str(out),
        "packs_in_response": len(preview),
        "packs_preview_only": len(preview) < len(packs),
        "packs": preview,
    }


def prepare_one(job_index: int) -> dict[str, Any]:
    scraped = _load_scraped_jobs()
    composed_list = _load_composed()
    if job_index < 0 or job_index >= len(scraped):
        raise ValueError(f"job_index out of range (0..{len(scraped) - 1})")
    if job_index >= len(composed_list):
        raise ValueError(f"No composed resume for job_index {job_index}")
    pack = build_pack(job_index, scraped[job_index], composed_list[job_index], _target_skill_count())
    return {"pack": pack}


def list_packs(offset: int = 0, limit: int = 50) -> dict[str, Any]:
    """Return a page of slim packs. The UI loops with offset until has_more is
    false, so any number of jobs stays well under the host RPC payload limit."""
    out = _path("RESUMATCH_PACKS_PATH", DEFAULT_PACKS_PATH)
    if not out.exists():
        return {"count": 0, "total": 0, "offset": 0, "has_more": False, "packs": [],
                "message": "No packs yet. Run action prepare_all."}
    raw = json.loads(out.read_text(encoding="utf-8"))
    all_packs = raw.get("packs") or []
    total = len(all_packs)
    offset = max(0, int(offset))
    limit = max(1, min(int(limit), 200))
    page = [_slim_pack(p) for p in all_packs[offset:offset + limit]]
    return {
        "count": total,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total,
        "prepared_at": raw.get("prepared_at"),
        "saved_to": str(out),
        "packs": page,
    }
