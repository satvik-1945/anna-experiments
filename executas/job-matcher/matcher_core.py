"""Score job listings against the saved ResuMatch profile."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESUMATCH_DIR = Path.home() / ".anna" / "resumatch"
DEFAULT_JOBS_PATH = RESUMATCH_DIR / "jobs_latest.json"
DEFAULT_MATCH_PATH = RESUMATCH_DIR / "match_results.json"
DEFAULT_PROFILE_PATH = RESUMATCH_DIR / "profile.json"

SENIORITY_RANK = {
    "intern": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
    "manager": 5,
    "director": 6,
}

_SKILL_RE = re.compile(
    r"\b(python|java|javascript|typescript|react|node|sql|aws|docker|kubernetes|"
    r"git|linux|fastapi|django|flask|pandas|numpy|machine learning|llm|ai|"
    r"excel|sap|tally|gst|audit|accounting|banking|teaching|nursing|"
    r"tensorflow|pytorch|rust|go|c\+\+|azure|gcp|terraform|agile|scrum|"
    r"\.net|vue|angular|salesforce|servicenow)\b",
    re.I,
)


@dataclass
class ScoredJob:
    job: dict[str, Any]
    score: float
    passed: bool
    skill_score: float
    text_score: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "job": self.job,
            "score": round(self.score, 1),
            "passed": self.passed,
            "skill_score": round(self.skill_score, 1),
            "text_score": round(self.text_score, 1),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "notes": self.notes,
        }


def _path(env_key: str, default: Path) -> Path:
    override = os.environ.get(env_key, "").strip()
    return Path(override) if override else default


def extract_skills(text: str) -> set[str]:
    return {m.group(0).lower() for m in _SKILL_RE.finditer(text)}


def _infer_job_seniority(title: str) -> str | None:
    t = title.lower()
    for level in ("director", "manager", "lead", "senior", "junior", "intern"):
        if level in t:
            return level
    return None


def _seniority_note(profile_seniority: str, job_title: str) -> str:
    job_level = _infer_job_seniority(job_title)
    if not job_level:
        return ""
    p_rank = SENIORITY_RANK.get(profile_seniority, 2)
    j_rank = SENIORITY_RANK.get(job_level, 2)
    if j_rank > p_rank + 1:
        return f"Job looks {job_level}-level; your profile is {profile_seniority} — apply only if stretch role."
    if j_rank < p_rank - 1:
        return f"Job may be below your {profile_seniority} level — still OK if you want volume."
    return ""


def load_profile() -> dict[str, Any]:
    path = _path("RESUMATCH_PROFILE_PATH", DEFAULT_PROFILE_PATH)
    if not path.exists():
        raise ValueError(
            f"No profile at {path}. Run user_profile action save first."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("profile") or raw


def load_jobs(jobs_path: Path | None = None) -> list[dict[str, Any]]:
    path = jobs_path or _path("RESUMATCH_JOBS_PATH", DEFAULT_JOBS_PATH)
    if not path.exists():
        raise ValueError(
            f"No jobs file at {path}. Scrape with job_scraper and persist:true first."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    jobs = raw.get("jobs")
    if isinstance(jobs, list):
        return jobs
    raise ValueError(f"Invalid jobs file format at {path}")


def _text_similarity(resume_text: str, job: dict[str, Any]) -> float:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    job_text = f"{job.get('title', '')}\n{job.get('company', '')}\n{job.get('description', '')}"
    if not resume_text.strip() or not job_text.strip():
        return 0.0
    matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(
        [resume_text, job_text]
    )
    return float(cosine_similarity(matrix[0:1], matrix[1:2]).flatten()[0] * 100)


def score_jobs(
    jobs: list[dict[str, Any]],
    profile: dict[str, Any],
    threshold: float = 80.0,
) -> list[ScoredJob]:
    resume_text = profile.get("resume_text") or ""
    profile_skills = set(profile.get("skills") or []) | extract_skills(resume_text)
    target_skills = set(profile.get("target_skills") or [])
    profile_seniority = profile.get("seniority", "mid")
    resume_blob = resume_text
    if profile_skills:
        resume_blob = f"{resume_text}\n{' '.join(sorted(profile_skills))}"

    results: list[ScoredJob] = []
    for job in jobs:
        blob = f"{job.get('title', '')} {job.get('description', '')}"
        job_skills = extract_skills(blob)
        matched = sorted(profile_skills & job_skills)
        missing = sorted(job_skills - profile_skills)

        if job_skills:
            job_cov = len(matched) / len(job_skills)
            prof_cov = len(matched) / max(len(profile_skills), 1)
            skill_score = (0.6 * job_cov + 0.4 * prof_cov) * 100
        else:
            skill_score = 50.0

        text_score = _text_similarity(resume_blob, job)
        score = 0.35 * text_score + 0.65 * skill_score
        if target_skills:
            target_hits = target_skills & job_skills
            target_score = (len(target_hits) / len(target_skills)) * 100
            score = 0.75 * score + 0.25 * target_score

        seniority_note = _seniority_note(profile_seniority, str(job.get("title", "")))
        if score >= threshold:
            notes = f"Strong match ({score:.0f}%) — good candidate for tailoring."
        else:
            notes = f"Below {threshold:.0f}% threshold — consider skipping."
        if seniority_note:
            notes = f"{notes} {seniority_note}"

        results.append(
            ScoredJob(
                job=job,
                score=score,
                passed=score >= threshold,
                skill_score=skill_score,
                text_score=text_score,
                matched_skills=matched,
                missing_skills=missing,
                notes=notes.strip(),
            )
        )

    results.sort(key=lambda item: item.score, reverse=True)
    return results


def run_match(
    threshold: float = 80.0,
    jobs_path: str | None = None,
    save: bool = True,
    ensure_passed: int = 0,
) -> dict[str, Any]:
    profile = load_profile()
    path = Path(jobs_path) if jobs_path else None
    jobs = load_jobs(path)
    if not jobs:
        raise ValueError(
            "No jobs to score — scrape returned 0 results. "
            "Use a shorter Indeed search (e.g. 'Python developer') in Profile."
        )
    scored = score_jobs(jobs, profile, threshold=threshold)
    strict_passed = [s for s in scored if s.passed]
    rejected = [s for s in scored if not s.passed]

    fallback_used = False
    passed = strict_passed
    if not passed and ensure_passed > 0:
        fallback_used = True
        passed = scored[:ensure_passed]
        for item in passed:
            item.passed = True
            item.notes = (
                f"Top match ({item.score:.0f}%) — shown for manual review "
                f"(below {threshold:.0f}% threshold)."
            )

    passed_dicts: list[dict[str, Any]] = []
    for item in passed:
        row = item.to_dict()
        if fallback_used and item.score < threshold:
            row["fallback"] = True
        passed_dicts.append(row)

    top_preview = [
        {
            "title": s.job.get("title"),
            "company": s.job.get("company"),
            "score": round(s.score, 1),
            "apply_url": s.job.get("apply_url"),
        }
        for s in scored[:5]
    ]

    payload = {
        "threshold": threshold,
        "total": len(scored),
        "passed_count": len(strict_passed),
        "rejected_count": len(rejected),
        "effective_passed_count": len(passed_dicts),
        "fallback_used": fallback_used,
        "ensure_passed": ensure_passed,
        "top_preview": top_preview,
        "scored_at": datetime.now(UTC).isoformat(),
        "results": [s.to_dict() for s in scored],
        "passed": passed_dicts,
    }

    if save:
        out = _path("RESUMATCH_MATCH_PATH", DEFAULT_MATCH_PATH)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["saved_to"] = str(out)

    return payload
