"""Tailor LaTeX resume Skills section per job description."""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESUMATCH_DIR = Path.home() / ".anna" / "resumatch"
DEFAULT_JOBS_PATH = RESUMATCH_DIR / "jobs_latest.json"
DEFAULT_PROFILE_PATH = RESUMATCH_DIR / "profile.json"
DEFAULT_RESUME_TEX_PATH = RESUMATCH_DIR / "resume_base.tex"
DEFAULT_OUTPUT_DIR = RESUMATCH_DIR / "resumes"
DEFAULT_PDF_DIR = RESUMATCH_DIR / "pdfs"
DEFAULT_DOWNLOADS_DIR = Path.home() / "Downloads"
BUNDLED_RESUME_CLS = Path(__file__).resolve().parent / "assets" / "resume.cls"
EXECUTA_DIR = Path(__file__).resolve().parent

SECTION_SKILLS_RE = re.compile(
    r"(\\section\{Skills\})(.*?)(?=\\section[\{\*])",
    re.DOTALL | re.IGNORECASE,
)

RSECTION_SKILLS_RE = re.compile(
    r"(\\begin\{rSection\}\{(?:Technical )?Skills\})(.*?)(\\end\{rSection\})",
    re.DOTALL | re.IGNORECASE,
)

ITEM_RE = re.compile(r"\\item\s+(.*)", re.DOTALL)
TABULAR_ROW_RE = re.compile(
    r"^(\s*.+?)\s*(?<!\\)&\s*(.+?)\s*\\\\\s*$",
    re.MULTILINE,
)

_SKILL_RE = re.compile(
    r"\b(python|java|javascript|typescript|react|node|sql|aws|docker|kubernetes|"
    r"git|linux|fastapi|django|flask|pandas|numpy|machine learning|llm|ai|rag|"
    r"mongodb|postgresql|redis|pytorch|huggingface|pydantic|angular|php|c\+\+|"
    r"tensorflow|rust|go|azure|gcp|terraform|agile|scrum|sagemaker|ner|"
    r"elasticsearch|nginx|caddy|sparql|openai|vector)\b",
    re.I,
)


@dataclass
class SkillsBlock:
    start: int
    end: int
    full: str
    inner: str
    fmt: str
    header: str
    footer: str


def _path(env_key: str, default: Path) -> Path:
    override = os.environ.get(env_key, "").strip()
    return Path(override) if override else default


def extract_skills(text: str) -> set[str]:
    return {m.group(0).lower() for m in _SKILL_RE.finditer(text)}


def slugify(title: str, company: str) -> str:
    raw = f"{title}_{company}".lower()
    slug = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return slug[:80] or "job"


def load_base_tex() -> str:
    profile_path = _path("RESUMATCH_PROFILE_PATH", DEFAULT_PROFILE_PATH)
    if profile_path.exists():
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
        data = raw.get("profile") or raw
        if data.get("resume_tex"):
            return str(data["resume_tex"])
    tex_path = _path("RESUMATCH_RESUME_TEX_PATH", DEFAULT_RESUME_TEX_PATH)
    if tex_path.exists():
        return tex_path.read_text(encoding="utf-8")
    raise ValueError(
        "No resume LaTeX found. Save profile with resume_latex (Overleaf paste) first."
    )


def load_scraped_jobs(limit: int | None = None) -> list[dict[str, Any]]:
    jobs_path = _path("RESUMATCH_JOBS_PATH", DEFAULT_JOBS_PATH)
    if not jobs_path.exists():
        raise ValueError("No jobs_latest.json — run job_scraper action scrape first.")
    raw = json.loads(jobs_path.read_text(encoding="utf-8"))
    jobs = list(raw.get("jobs") or [])
    if not jobs:
        raise ValueError("Scrape returned 0 jobs. Edit profile search query and sync again.")
    entries = [{"job": job} for job in jobs]
    if limit is not None:
        entries = entries[:limit]
    return entries


def load_passed_jobs(limit: int | None = None) -> list[dict[str, Any]]:
    """Alias for scraped jobs (legacy name used by compose_by_index)."""
    return load_scraped_jobs(limit=limit)


def find_skills_block(tex: str) -> SkillsBlock | None:
    m = RSECTION_SKILLS_RE.search(tex)
    if m:
        return SkillsBlock(
            start=m.start(),
            end=m.end(),
            full=m.group(0),
            inner=m.group(2),
            fmt="rsection",
            header=m.group(1),
            footer=m.group(3),
        )
    m = SECTION_SKILLS_RE.search(tex)
    if m:
        return SkillsBlock(
            start=m.start(),
            end=m.end(),
            full=m.group(0),
            inner=m.group(2),
            fmt="section",
            header=m.group(1),
            footer="",
        )
    return None


def _resume_skill_pool(base_tex: str) -> set[str]:
    return extract_skills(base_tex)


def _job_skills(job: dict[str, Any]) -> set[str]:
    blob = f"{job.get('title', '')} {job.get('description', '')}"
    return extract_skills(blob)


def _reorder_comma_list(value: str, job_skills: set[str]) -> str:
    parts = [p.strip().rstrip(".") for p in value.split(",") if p.strip()]
    if not parts:
        return value

    def score(part: str) -> tuple[int, str]:
        part_lower = part.lower()
        hits = sum(1 for skill in job_skills if skill in part_lower)
        return (-hits, part_lower)

    parts.sort(key=score)
    return ", ".join(parts)


def _reorder_item_line(item_line: str, job_skills: set[str]) -> str:
    if ":" not in item_line:
        return item_line
    label, rest = item_line.split(":", 1)
    return f"{label.strip()}: {_reorder_comma_list(rest, job_skills)}."


KEY_SKILLS_MAX_ITEMS = 7
KEY_SKILLS_MAX_CHARS = 72
KEY_SKILLS_MAX_TOKEN_LEN = 22


def _format_highlights(matched_skills: list[str]) -> str:
    """Comma-list that fits one tabular row without crossing the right margin."""
    if not matched_skills:
        return ""
    parts: list[str] = []
    total = 0
    for s in matched_skills:
        label = str(s).strip()
        if not label:
            continue
        label = label.title() if label.islower() else label
        if len(label) > KEY_SKILLS_MAX_TOKEN_LEN:
            continue
        sep = 2 if parts else 0
        if len(parts) >= KEY_SKILLS_MAX_ITEMS:
            break
        if total + sep + len(label) > KEY_SKILLS_MAX_CHARS:
            break
        parts.append(label)
        total += sep + len(label)
    return ", ".join(parts)


def build_skills_section_itemize(
    original_inner: str,
    job: dict[str, Any],
    matched_skills: list[str] | None = None,
    resume_pool: set[str] | None = None,
) -> str:
    job_skills = _job_skills(job)
    items = ITEM_RE.findall(original_inner)
    if not items:
        raise ValueError("Could not parse \\item lines in Skills section")

    pool = resume_pool or set()
    highlights = matched_skills or sorted(job_skills & pool) or sorted(job_skills)
    highlight_line = ""
    if highlights:
        highlight_line = (
            f"\\item \\textbf{{Key Skills:}} {_format_highlights(highlights)}.\n"
        )

    tailored_items: list[str] = []
    for item in items:
        low = item.lower()
        if "key skills:" in low or "role-aligned highlights" in low:
            continue
        tailored_items.append(_reorder_item_line(item.strip(), job_skills))

    body = highlight_line + "".join(f"\\item {line}\n" for line in tailored_items)
    replacement = "\\begin{itemize}\n" + body + "\\end{itemize}"
    if "\\begin{itemize}" in original_inner:
        return re.sub(
            r"\\begin\{itemize\}.*?\\end\{itemize\}",
            lambda _m: replacement,
            original_inner,
            count=1,
            flags=re.DOTALL,
        )
    return f"\n{replacement}\n"


def build_skills_section_tabular(
    original_inner: str,
    job: dict[str, Any],
    matched_skills: list[str] | None = None,
) -> str:
    job_skills = _job_skills(job)
    highlights = matched_skills or sorted(job_skills)
    highlight_row = ""
    if highlights:
        highlight_row = f"Key Skills & {_format_highlights(highlights)} \\\\\n"

    def repl_row(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        low = label.lower()
        if "key skills" in low or "role-aligned" in low:
            return match.group(0)
        value = _reorder_comma_list(match.group(2), job_skills)
        return f"{label} & {value} \\\\\n"

    inner = original_inner
    if highlight_row and "key skills" not in inner.lower() and "role-aligned" not in inner.lower():
        inner = re.sub(
            r"(\\begin\{tabular\}[^\n]*\n)",
            lambda m: m.group(1) + highlight_row,
            inner,
            count=1,
            flags=re.IGNORECASE,
        )
    return TABULAR_ROW_RE.sub(repl_row, inner)


def build_tailored_skills_block(
    block: SkillsBlock,
    job: dict[str, Any],
    matched_skills: list[str] | None,
    resume_tex: str,
) -> str:
    pool = matched_skills or sorted(_job_skills(job) & _resume_skill_pool(resume_tex))
    if block.fmt == "rsection":
        inner = build_skills_section_tabular(block.inner, job, pool)
        return f"{block.header}{inner}\n{block.footer}\n"
    inner = build_skills_section_itemize(
        block.inner, job, pool, resume_pool=_resume_skill_pool(resume_tex)
    )
    return f"{block.header}{inner}\n"


def replace_skills_section(tex: str, new_section: str) -> str:
    block = find_skills_block(tex)
    if not block:
        raise ValueError(
            "Resume must contain a Skills block: \\section{Skills} or "
            "\\begin{rSection}{Technical Skills} ... \\end{rSection}"
        )
    return tex[: block.start] + new_section + tex[block.end :]


def compose_for_job(
    entry: dict[str, Any],
    base_tex: str | None = None,
    key_skills: list[str] | None = None,
) -> dict[str, Any]:
    tex = base_tex or load_base_tex()
    job = entry.get("job") or entry
    if key_skills:
        # LLM-extracted key skills from the JD — used verbatim (no intersection
        # with the resume), so the "Key Skills" line reflects the real role.
        matched = [str(s).strip() for s in key_skills if str(s).strip()]
    else:
        matched = entry.get("matched_skills") or sorted(_job_skills(job) & _resume_skill_pool(tex))

    block = find_skills_block(tex)
    if not block:
        raise ValueError(
            "Could not find Skills in resume LaTeX. Supported: \\section{Skills} or "
            "\\begin{rSection}{Technical Skills}"
        )

    new_section = build_tailored_skills_block(block, job, matched, tex)
    tailored = replace_skills_section(tex, new_section)

    out_dir = _path("RESUMATCH_RESUMES_DIR", DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(str(job.get("title", "job")), str(job.get("company", "company")))
    out_path = out_dir / f"resume_{slug}.tex"
    out_path.write_text(tailored, encoding="utf-8")

    return {
        "job_title": job.get("title"),
        "company": job.get("company"),
        "apply_url": job.get("apply_url"),
        "output_path": str(out_path),
        "matched_skills_used": matched,
        "skills_format": block.fmt,
        "composed_at": datetime.now(UTC).isoformat(),
        "note": "Only Skills section changed. Review before applying — do not claim skills you cannot defend.",
    }


def compose_all(*, max_response_resumes: int = 5) -> dict[str, Any]:
    passed = load_passed_jobs()
    base = load_base_tex()
    results = [compose_for_job(entry, base_tex=base) for entry in passed]
    manifest_path = _path("RESUMATCH_RESUMES_DIR", DEFAULT_OUTPUT_DIR) / "manifest.json"
    manifest_path.write_text(
        json.dumps({"composed_at": datetime.now(UTC).isoformat(), "resumes": results}, indent=2),
        encoding="utf-8",
    )
    preview = [
        {
            "job_title": r.get("job_title"),
            "company": r.get("company"),
            "output_path": r.get("output_path"),
            "matched_skills_used": r.get("matched_skills_used"),
        }
        for r in results[: max(0, max_response_resumes)]
    ]
    return {
        "count": len(results),
        "manifest_path": str(manifest_path),
        "resumes_in_response": len(preview),
        "resumes_preview_only": len(preview) < len(results),
        "resumes": preview,
    }


def compose_by_index(job_index: int) -> dict[str, Any]:
    passed = load_passed_jobs()
    if job_index < 0 or job_index >= len(passed):
        raise ValueError(f"job_index out of range (0..{len(passed) - 1})")
    return compose_for_job(passed[job_index])


def _find_tectonic() -> str:
    for name in ("tectonic", "tecto"):
        found = shutil.which(name)
        if found:
            return found
    candidates: list[Path] = []
    exe = Path(sys.executable)
    for bin_dir in (exe.parent, exe.resolve().parent):
        for name in ("tectonic", "tecto"):
            candidates.append(bin_dir / name)
    venv_bin = EXECUTA_DIR / ".venv" / "bin"
    for name in ("tectonic", "tecto"):
        candidates.append(venv_bin / name)
    env_bin = os.environ.get("RESUMATCH_TECTONIC", "").strip()
    if env_bin:
        candidates.insert(0, Path(env_bin))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise ValueError(
        "PDF engine not found. In executas/resume-composer run: uv sync (installs tecto)."
    )


def _pdf_download_name(job_title: str | None, company: str | None) -> str:
    raw = f"Resume_{company or 'job'}_{job_title or 'role'}"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("_")
    return (safe[:120] or "resume") + ".pdf"


def _ensure_resume_cls(work_dir: Path, tex: str) -> None:
    if r"\documentclass{resume}" not in tex:
        return
    target = work_dir / "resume.cls"
    if target.exists():
        return
    if BUNDLED_RESUME_CLS.is_file():
        shutil.copy2(BUNDLED_RESUME_CLS, target)
        return
    raise ValueError("resume.cls missing — reinstall resume-composer executa.")


def _write_base_tex() -> Path:
    """Persist the profile's base resume LaTeX to a file for compilation."""
    out_dir = _path("RESUMATCH_RESUMES_DIR", DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_path = out_dir / "resume_base.tex"
    base_path.write_text(load_base_tex(), encoding="utf-8")
    return base_path


def _resolve_tex_path(
    *,
    job_index: int | None,
    tex_path: str | Path | None,
    base: bool = False,
) -> tuple[Path, dict[str, Any] | None]:
    if base:
        return _write_base_tex(), None

    if tex_path is not None:
        path = Path(tex_path).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Resume .tex not found: {path}")
        return path, None

    if job_index is None:
        raise ValueError("compile_pdf requires job_index or tex_path")

    passed = load_passed_jobs()
    if job_index < 0 or job_index >= len(passed):
        raise ValueError(f"job_index out of range (0..{len(passed) - 1})")

    entry = passed[job_index]
    job = entry.get("job") or entry
    slug = slugify(str(job.get("title", "job")), str(job.get("company", "company")))
    out_dir = _path("RESUMATCH_RESUMES_DIR", DEFAULT_OUTPUT_DIR)
    path = out_dir / f"resume_{slug}.tex"
    if not path.is_file():
        result = compose_for_job(entry)
        path = Path(result["output_path"])
    return path, entry


def _fix_tex_for_tectonic(tex: str) -> str:
    """Reorder hyperref for Tectonic/XeTeX — must load after geometry with hidelinks."""
    if "\\begin{document}" not in tex:
        return tex
    if "\\usepackage" not in tex and "\\href" not in tex:
        return tex
    stripped = re.sub(
        r"\\usepackage(?:\[[^\]]*\])?\{hyperref\}\s*\n?",
        "",
        tex,
    )
    return stripped.replace(
        "\\begin{document}",
        "\\usepackage[hidelinks,unicode]{hyperref}\n\\begin{document}",
        1,
    )


def compile_pdf(
    *,
    job_index: int | None = None,
    tex_path: str | Path | None = None,
    job_title: str | None = None,
    company: str | None = None,
    base: bool = False,
    to_downloads: bool = True,
    key_skills: list[str] | None = None,
) -> dict[str, Any]:
    if key_skills and not base and tex_path is None and job_index is not None:
        # Re-tailor this job with the LLM-extracted key skills before compiling.
        passed = load_passed_jobs()
        if job_index < 0 or job_index >= len(passed):
            raise ValueError(f"job_index out of range (0..{len(passed) - 1})")
        entry = passed[job_index]
        result = compose_for_job(entry, key_skills=list(key_skills))
        path = Path(result["output_path"])
    else:
        path, entry = _resolve_tex_path(job_index=job_index, tex_path=tex_path, base=base)
    tex = _fix_tex_for_tectonic(path.read_text(encoding="utf-8"))
    work_dir = path.parent
    _ensure_resume_cls(work_dir, tex)

    build_path = work_dir / f"{path.stem}_build.tex"
    build_path.write_text(tex, encoding="utf-8")

    tectonic = _find_tectonic()
    proc = subprocess.run(
        [tectonic, "-X", "compile", build_path.name],
        cwd=work_dir,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "tectonic failed").strip()
        raise ValueError(f"PDF compile failed: {detail[-500:]}")

    pdf_src = work_dir / f"{build_path.stem}.pdf"
    if not pdf_src.is_file():
        raise ValueError("PDF compile finished but no .pdf file was produced.")

    job = (entry or {}).get("job") or entry or {}
    filename = _pdf_download_name(
        str(job_title or job.get("title") or path.stem),
        str(company or job.get("company") or ""),
    )

    pdf_dir = _path("RESUMATCH_PDF_DIR", DEFAULT_PDF_DIR)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_dest = pdf_dir / filename
    shutil.copy2(pdf_src, pdf_dest)

    downloads_path: str | None = None
    if to_downloads:
        downloads_dir = _path("RESUMATCH_DOWNLOADS_DIR", DEFAULT_DOWNLOADS_DIR)
        try:
            downloads_dir.mkdir(parents=True, exist_ok=True)
            downloads_dest = downloads_dir / filename
            shutil.copy2(pdf_src, downloads_dest)
            downloads_path = str(downloads_dest)
        except OSError:
            downloads_path = None

    payload = pdf_dest.read_bytes()
    return {
        "job_index": job_index,
        "tex_path": str(path),
        "pdf_path": str(pdf_dest),
        "downloads_path": downloads_path,
        "pdf_filename": filename,
        "pdf_base64": base64.b64encode(payload).decode("ascii"),
        "size_bytes": len(payload),
        "compiled_at": datetime.now(UTC).isoformat(),
    }
