"""ResuMatch user profile — local store (APS-ready schema)."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROFILE_VERSION = 2
DEFAULT_PROFILE_DIR = Path.home() / ".anna" / "resumatch"
DEFAULT_PROFILE_PATH = DEFAULT_PROFILE_DIR / "profile.json"
DEFAULT_RESUME_TEX_PATH = DEFAULT_PROFILE_DIR / "resume_base.tex"

# Domains the user picks explicitly; drives search_term defaults.
JOB_DOMAINS: dict[str, str] = {
    "software_engineering": "software engineer",
    "data_science": "data scientist",
    "machine_learning": "machine learning engineer",
    "devops": "devops engineer",
    "product_management": "product manager",
    "accounting": "accountant",
    "taxation": "tax analyst",
    "banking": "banking officer",
    "teaching": "teacher",
    "nursing": "registered nurse",
    "cleaning_hospitality": "housekeeping staff",
    "sales": "sales executive",
    "marketing": "marketing manager",
    "other": "professional",
}

SENIORITY_LEVELS = ("intern", "junior", "mid", "senior", "lead", "manager", "director")


@dataclass
class UserProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    domain: str = "software_engineering"
    seniority: str = "mid"
    years_experience: int = 0
    location: str = "India"
    search_term: str = ""
    target_skills: list[str] = field(default_factory=list)
    resume_summary: str = ""
    resume_text: str = ""
    resume_tex: str = ""
    resume_path: str = ""
    resume_tex_path: str = ""
    skills: list[str] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def effective_search_term(self) -> str:
        if self.search_term.strip():
            return self.search_term.strip()
        parts: list[str] = []
        if self.seniority in ("intern", "junior"):
            parts.append(self.seniority)
        elif self.seniority in ("senior", "lead", "manager", "director"):
            parts.append("senior")
        skill_pool = self.target_skills or self.skills
        for skill in skill_pool[:3]:
            if skill.lower() not in " ".join(parts).lower():
                parts.append(skill)
        base = JOB_DOMAINS.get(self.domain, JOB_DOMAINS["other"])
        if not parts:
            return base
        if base.split()[-1] not in " ".join(parts).lower():
            parts.append(base.split()[-1] if " " in base else base)
        return " ".join(parts[:6])

    def scrape_search_term(self) -> str:
        """Short Indeed-friendly query (user may enter a long title list)."""
        raw = self.search_term.strip() if self.search_term.strip() else self.effective_search_term()
        return normalize_search_query(raw)


def profile_path() -> Path:
    override = os.environ.get("RESUMATCH_PROFILE_PATH", "").strip()
    return Path(override) if override else DEFAULT_PROFILE_PATH


def _skill_pattern() -> re.Pattern[str]:
    return re.compile(
        r"\b(python|java|javascript|typescript|react|node|sql|aws|docker|kubernetes|"
        r"git|linux|fastapi|django|flask|pandas|numpy|machine learning|llm|ai|"
        r"excel|sap|tally|gst|audit|accounting|banking|teaching|nursing|"
        r"tensorflow|pytorch|rust|go|c\+\+|azure|gcp|terraform|agile|scrum)\b",
        re.I,
    )


def extract_skills_from_text(text: str) -> list[str]:
    seen: set[str] = set()
    skills: list[str] = []
    for match in _skill_pattern().finditer(text):
        skill = match.group(0).lower()
        if skill not in seen:
            seen.add(skill)
            skills.append(skill)
    return skills


def extract_contact(text: str) -> dict[str, str]:
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(\+?\d[\d\s\-().]{8,}\d)", text)
    name = ""
    for line in text.splitlines():
        line = line.strip()
        if line and len(line) < 80 and "@" not in line:
            name = line
            break
    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
    }


def _strip_latex(tex: str) -> str:
    """Rough plain-text extraction for skill matching."""
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", tex)
    text = re.sub(r"[{}\\]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def derive_resume_summary(text: str, max_len: int = 480) -> str:
    """Short gist from resume plain text for search + display (no LLM)."""
    if not text.strip():
        return ""
    cleaned = re.sub(r"\s+", " ", text).strip()
    for marker in (
        "work experience",
        "experience",
        "professional experience",
        "employment",
    ):
        idx = cleaned.lower().find(marker)
        if idx >= 0:
            snippet = cleaned[idx : idx + max_len * 2]
            break
    else:
        snippet = cleaned[: max_len * 2]
    # Prefer sentence-like chunks over LaTeX debris.
    snippet = re.sub(r"[^\w\s@.,+\-/%]", " ", snippet, flags=re.UNICODE)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    if len(snippet) <= max_len:
        return snippet
    cut = snippet[:max_len].rsplit(" ", 1)[0]
    return (cut or snippet[:max_len]).strip() + "…"


def parse_skill_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        items = [str(x).strip().lower() for x in raw if str(x).strip()]
    else:
        items = [p.strip().lower() for p in str(raw).split(",") if p.strip()]
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def build_profile(
    *,
    domain: str,
    seniority: str,
    years_experience: int,
    location: str,
    resume_text: str = "",
    resume_latex: str = "",
    resume_path: str = "",
    resume_tex_path_arg: str = "",
    search_term: str = "",
    target_skills: list[str] | str | None = None,
    name: str = "",
    email: str = "",
    phone: str = "",
) -> UserProfile:
    if domain not in JOB_DOMAINS:
        raise ValueError(f"unknown domain: {domain}. Choose one of: {', '.join(JOB_DOMAINS)}")

    if seniority not in SENIORITY_LEVELS:
        raise ValueError(f"unknown seniority: {seniority}. Choose one of: {', '.join(SENIORITY_LEVELS)}")

    if years_experience < 0:
        raise ValueError("years_experience must be >= 0")

    tex = (resume_latex or "").strip()
    if not tex and resume_tex_path_arg:
        tp = Path(resume_tex_path_arg)
        if not tp.exists():
            raise ValueError(f"resume_tex_path not found: {resume_tex_path_arg}")
        tex = tp.read_text(encoding="utf-8", errors="replace")

    text = resume_text.strip()
    if not text and resume_path:
        path = Path(resume_path)
        if not path.exists():
            raise ValueError(f"resume_path not found: {resume_path}")
        text = path.read_text(encoding="utf-8", errors="replace")

    if tex and not text:
        text = _strip_latex(tex)

    if not tex and not text:
        raise ValueError("provide resume_latex (Overleaf .tex paste), resume_tex_path, or resume_text")

    contact = extract_contact(text) if text else {"name": "", "email": "", "phone": ""}
    skills = extract_skills_from_text(text) if text else []
    if tex:
        skills = sorted(set(skills) | set(extract_skills_from_text(_strip_latex(tex))))

    parsed_targets = parse_skill_list(target_skills)
    summary = derive_resume_summary(text)

    profile = UserProfile(
        name=name or contact["name"],
        email=email or contact["email"],
        phone=phone or contact["phone"],
        domain=domain,
        seniority=seniority,
        years_experience=years_experience,
        location=location.strip() or "India",
        search_term=search_term.strip(),
        target_skills=parsed_targets,
        resume_summary=summary,
        resume_text=text,
        resume_tex=tex,
        resume_path=resume_path,
        resume_tex_path=resume_tex_path_arg,
        skills=skills,
        updated_at=datetime.now(UTC).isoformat(),
    )
    return profile


def resume_tex_path() -> Path:
    override = os.environ.get("RESUMATCH_RESUME_TEX_PATH", "").strip()
    return Path(override) if override else DEFAULT_RESUME_TEX_PATH


def save_profile(profile: UserProfile) -> Path:
    path = profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if profile.resume_tex.strip():
        tex_out = resume_tex_path()
        tex_out.parent.mkdir(parents=True, exist_ok=True)
        tex_out.write_text(profile.resume_tex, encoding="utf-8")
    payload = {
        "schema_version": PROFILE_VERSION,
        "profile": profile.to_dict(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_profile() -> UserProfile | None:
    path = profile_path()
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    schema = raw.get("schema_version", 1)
    if schema not in (1, PROFILE_VERSION):
        return None
    data = raw.get("profile") or raw
    profile = UserProfile(**{k: v for k, v in data.items() if k in UserProfile.__dataclass_fields__})
    if not profile.resume_tex.strip():
        tex_file = resume_tex_path()
        if tex_file.exists():
            profile.resume_tex = tex_file.read_text(encoding="utf-8")
    return profile


def normalize_search_query(query: str, max_words: int = 4) -> str:
    """Indeed works best with short queries — long title lists return 0 results."""
    q = query.strip()
    if not q:
        return q
    if "," in q:
        q = q.split(",")[0].strip()
    words = q.split()
    if len(words) > max_words:
        q = " ".join(words[:max_words])
    return q


def profile_is_complete(profile: UserProfile) -> bool:
    """Profile must have name, search query, resume, and target skills."""
    return bool(
        profile.name.strip()
        and profile.search_term.strip()
        and profile.resume_tex.strip()
        and (profile.target_skills or profile.skills)
    )


def profile_for_scraper() -> dict[str, Any]:
    """Defaults job-scraper can merge into scrape args."""
    profile = load_profile()
    if profile is None:
        return {}
    return {
        "search_term": profile.scrape_search_term(),
        "search_term_full": profile.search_term.strip() or profile.effective_search_term(),
        "location": profile.location,
        "profile_loaded": True,
        "domain": profile.domain,
        "seniority": profile.seniority,
        "years_experience": profile.years_experience,
        "skills": profile.skills,
        "target_skills": profile.target_skills,
        "resume_summary": profile.resume_summary,
    }
