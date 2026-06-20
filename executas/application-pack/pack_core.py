"""Build manual-apply packs: job link + tailored resume path. No email draft."""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESUMATCH_DIR = Path.home() / ".anna" / "resumatch"
DEFAULT_MATCH_PATH = RESUMATCH_DIR / "match_results.json"
DEFAULT_RESUMES_DIR = RESUMATCH_DIR / "resumes"
DEFAULT_MANIFEST_PATH = DEFAULT_RESUMES_DIR / "manifest.json"
DEFAULT_PACKS_PATH = RESUMATCH_DIR / "application_packs.json"


def _path(env_key: str, default: Path) -> Path:
    override = os.environ.get(env_key, "").strip()
    return Path(override) if override else default


def _load_passed() -> list[dict[str, Any]]:
    match_path = _path("RESUMATCH_MATCH_PATH", DEFAULT_MATCH_PATH)
    if not match_path.exists():
        raise ValueError("No match_results.json — run job_matcher action score first.")
    raw = json.loads(match_path.read_text(encoding="utf-8"))
    passed = list(raw.get("passed") or [])
    if not passed:
        results = raw.get("results") or []
        cap = int(raw.get("ensure_passed") or 15) or 15
        if results:
            passed = results[:cap]
        else:
            raise ValueError("No passed jobs. Run matcher or lower threshold.")
    return passed


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


def build_pack(job_index: int, passed_entry: dict[str, Any], composed: dict[str, Any]) -> dict[str, Any]:
    job = passed_entry.get("job") or {}
    return {
        "job_index": job_index,
        "job_title": job.get("title") or composed.get("job_title"),
        "company": job.get("company") or composed.get("company"),
        "apply_url": job.get("apply_url") or composed.get("apply_url"),
        "location": job.get("location", ""),
        "source": job.get("source", ""),
        "match_score": passed_entry.get("score"),
        "resume_tex_path": composed.get("output_path"),
        "matched_skills": passed_entry.get("matched_skills") or composed.get("matched_skills_used"),
        "checklist": _checklist(
            str(job.get("apply_url") or composed.get("apply_url") or ""),
            str(composed.get("output_path") or ""),
        ),
    }


def prepare_all() -> dict[str, Any]:
    passed = _load_passed()
    composed_list = _load_composed()
    if len(composed_list) < len(passed):
        raise ValueError(
            f"Only {len(composed_list)} composed resumes for {len(passed)} passed jobs. "
            "Run resume_composer compose_all."
        )

    packs = [
        build_pack(i, passed[i], composed_list[i])
        for i in range(len(passed))
    ]
    payload = {
        "prepared_at": datetime.now(UTC).isoformat(),
        "count": len(packs),
        "packs": packs,
    }
    out = _path("RESUMATCH_PACKS_PATH", DEFAULT_PACKS_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["saved_to"] = str(out)
    return payload


def prepare_one(job_index: int) -> dict[str, Any]:
    passed = _load_passed()
    composed_list = _load_composed()
    if job_index < 0 or job_index >= len(passed):
        raise ValueError(f"job_index out of range (0..{len(passed) - 1})")
    if job_index >= len(composed_list):
        raise ValueError(f"No composed resume for job_index {job_index}")
    pack = build_pack(job_index, passed[job_index], composed_list[job_index])
    return {"pack": pack}


def list_packs() -> dict[str, Any]:
    out = _path("RESUMATCH_PACKS_PATH", DEFAULT_PACKS_PATH)
    if not out.exists():
        return {"count": 0, "packs": [], "message": "No packs yet. Run action prepare_all."}
    raw = json.loads(out.read_text(encoding="utf-8"))
    preview = [
        {
            "job_index": p.get("job_index"),
            "job_title": p.get("job_title"),
            "company": p.get("company"),
            "apply_url": p.get("apply_url"),
            "match_score": p.get("match_score"),
            "resume_tex_path": p.get("resume_tex_path"),
        }
        for p in raw.get("packs") or []
    ]
    return {
        "count": raw.get("count", len(preview)),
        "prepared_at": raw.get("prepared_at"),
        "saved_to": str(out),
        "packs": preview,
    }
