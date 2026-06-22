"""Shared job scraping logic for ResuMatch (JobSpy + free APIs)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests
from jobspy import scrape_jobs

from scraper_filters import filter_jobs_by_seniority


@dataclass
class JobRecord:
    source: str
    source_type: str
    title: str
    company: str
    location: str
    published_at: str
    apply_url: str
    description: str
    tags: list[str]
    fetched_at: str


@dataclass
class ScrapeConfig:
    mode: str = "free"
    search_term: str = "software engineer"
    location: str = "India"
    hours_old: int = 24
    results_wanted: int = 500
    country_indeed: str = "India"
    include_free_apis: bool = True
    proxies: list[str] = field(default_factory=list)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    text = str(value).strip()
    if not text:
        return None

    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except ValueError:
        pass

    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except (TypeError, ValueError):
        return None


def _within_hours(value: Any, hours: int) -> bool:
    dt = _parse_dt(value)
    if dt is None:
        return False
    return dt >= datetime.now(UTC) - timedelta(hours=hours)


def _safe_get(row: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return _normalize_text(value)
    return ""


def fetch_jobspy_jobs(
    *,
    search_term: str,
    location: str,
    results_wanted: int,
    hours_old: int,
    country_indeed: str,
    include_linkedin: bool,
    proxies: list[str] | None,
) -> list[JobRecord]:
    sites = ["indeed", "google"]
    if include_linkedin:
        sites.append("linkedin")

    kwargs: dict[str, Any] = {
        "site_name": sites,
        "search_term": search_term,
        "location": location,
        "results_wanted": results_wanted,
        "hours_old": hours_old,
        "country_indeed": country_indeed,
    }
    if proxies:
        kwargs["proxies"] = proxies

    jobs_df = scrape_jobs(**kwargs)
    rows = jobs_df.to_dict(orient="records")
    fetched_at = _now_iso()
    normalized: list[JobRecord] = []

    for row in rows:
        source = _safe_get(row, ["site", "site_name"]) or "jobspy"
        published_at = _safe_get(
            row,
            ["date_posted", "listed_at", "posted_at", "created_at", "date"],
        )
        normalized.append(
            JobRecord(
                source=source,
                source_type="board",
                title=_safe_get(row, ["title"]),
                company=_safe_get(row, ["company", "company_name"]),
                location=_safe_get(row, ["location"]),
                published_at=published_at,
                apply_url=_safe_get(row, ["job_url_direct", "job_url", "url"]),
                description=_safe_get(row, ["description"]),
                tags=[],
                fetched_at=fetched_at,
            )
        )
    return normalized


def fetch_remotive_jobs(search_term: str, hours: int) -> list[JobRecord]:
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url, params={"search": search_term}, timeout=20)
    response.raise_for_status()
    payload = response.json()
    jobs = payload.get("jobs", [])
    fetched_at = _now_iso()
    out: list[JobRecord] = []
    for item in jobs:
        published_at = _normalize_text(item.get("publication_date"))
        if not _within_hours(published_at, hours):
            continue
        out.append(
            JobRecord(
                source="remotive",
                source_type="api",
                title=_normalize_text(item.get("title")),
                company=_normalize_text(item.get("company_name")),
                location=_normalize_text(item.get("candidate_required_location")),
                published_at=published_at,
                apply_url=_normalize_text(item.get("url")),
                description=_normalize_text(item.get("description")),
                tags=[_normalize_text(tag) for tag in item.get("tags", []) if tag],
                fetched_at=fetched_at,
            )
        )
    return out


def fetch_remoteok_jobs(search_term: str, hours: int) -> list[JobRecord]:
    url = "https://remoteok.com/api"
    response = requests.get(url, timeout=20, headers={"Accept": "application/json"})
    response.raise_for_status()
    payload = response.json()
    items = payload[1:] if isinstance(payload, list) else []
    query = search_term.lower().strip()
    fetched_at = _now_iso()
    out: list[JobRecord] = []
    for item in items:
        title = _normalize_text(item.get("position"))
        description = _normalize_text(item.get("description"))
        if query and query not in f"{title} {description}".lower():
            continue
        published_at = _normalize_text(item.get("date") or item.get("epoch"))
        if not _within_hours(published_at, hours):
            continue
        out.append(
            JobRecord(
                source="remoteok",
                source_type="api",
                title=title,
                company=_normalize_text(item.get("company")),
                location=_normalize_text(item.get("location") or "Remote"),
                published_at=published_at,
                apply_url=_normalize_text(item.get("url")),
                description=description,
                tags=[_normalize_text(tag) for tag in item.get("tags", []) if tag],
                fetched_at=fetched_at,
            )
        )
    return out


def fetch_arbeitnow_jobs(search_term: str, hours: int) -> list[JobRecord]:
    url = "https://arbeitnow.com/api/job-board-api"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    payload = response.json()
    items = payload.get("data", [])
    query = search_term.lower().strip()
    fetched_at = _now_iso()
    out: list[JobRecord] = []
    for item in items:
        title = _normalize_text(item.get("title"))
        description = _normalize_text(item.get("description"))
        if query and query not in f"{title} {description}".lower():
            continue
        published_at = _normalize_text(item.get("created_at"))
        if not _within_hours(published_at, hours):
            continue
        out.append(
            JobRecord(
                source="arbeitnow",
                source_type="api",
                title=title,
                company=_normalize_text(item.get("company_name")),
                location=_normalize_text(item.get("location")),
                published_at=published_at,
                apply_url=_normalize_text(item.get("url")),
                description=description,
                tags=[_normalize_text(tag) for tag in item.get("tags", []) if tag],
                fetched_at=fetched_at,
            )
        )
    return out


def dedupe_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    seen: set[str] = set()
    out: list[JobRecord] = []
    for job in jobs:
        key = "|".join(
            [
                job.apply_url.lower().strip(),
                job.title.lower().strip(),
                job.company.lower().strip(),
            ]
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(job)
    return out


def write_jobs_json(path: Path, jobs: list[JobRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(job) for job in jobs]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_proxy_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def run_scrape(config: ScrapeConfig, *, seniority_filter: str | None = None) -> dict[str, Any]:
    mode = (config.mode or "free").lower()
    if mode not in {"free", "boost"}:
        raise ValueError("mode must be 'free' or 'boost'")
    if config.hours_old < 1:
        raise ValueError("hours_old must be at least 1")
    if config.results_wanted < 1:
        raise ValueError("results_wanted must be at least 1")

    include_linkedin = mode == "boost"
    jobs: list[JobRecord] = []
    api_errors: list[str] = []

    if config.include_free_apis:
        for fn in (fetch_remotive_jobs, fetch_remoteok_jobs, fetch_arbeitnow_jobs):
            try:
                jobs.extend(fn(config.search_term, config.hours_old))
            except requests.RequestException as exc:
                api_errors.append(f"{fn.__name__}: {exc}")

    jobs.extend(
        fetch_jobspy_jobs(
            search_term=config.search_term,
            location=config.location,
            results_wanted=config.results_wanted,
            hours_old=config.hours_old,
            country_indeed=config.country_indeed,
            include_linkedin=include_linkedin,
            proxies=config.proxies or None,
        )
    )

    deduped = dedupe_jobs(jobs)
    before_filter = len(deduped)
    filtered = filter_jobs_by_seniority(deduped, seniority_filter)
    by_source: dict[str, int] = {}
    for job in filtered:
        by_source[job.source] = by_source.get(job.source, 0) + 1

    return {
        "mode": mode,
        "search_term": config.search_term,
        "location": config.location,
        "hours_old": config.hours_old,
        "seniority_filter": seniority_filter or "any",
        "count_before_seniority_filter": before_filter,
        "count": len(filtered),
        "by_source": by_source,
        "apply_url_coverage": round(
            100 * sum(1 for j in filtered if j.apply_url) / len(filtered),
            1,
        )
        if filtered
        else 0.0,
        "api_errors": api_errors,
        "linkedin_included": include_linkedin,
        "fetched_at": _now_iso(),
        "jobs_all": [asdict(job) for job in deduped],
        "jobs": [asdict(job) for job in filtered],
    }


def jobs_from_dicts(items: list[dict[str, Any]]) -> list[JobRecord]:
    return [
        JobRecord(
            source=str(j.get("source", "")),
            source_type=str(j.get("source_type", "board")),
            title=str(j.get("title", "")),
            company=str(j.get("company", "")),
            location=str(j.get("location", "")),
            published_at=str(j.get("published_at", "")),
            apply_url=str(j.get("apply_url", "")),
            description=str(j.get("description", "")),
            tags=list(j.get("tags") or []),
            fetched_at=str(j.get("fetched_at", "")),
        )
        for j in items
    ]


def refilter_cached_jobs(
    cache_payload: dict[str, Any],
    seniority_filter: str | None,
) -> dict[str, Any]:
    raw_jobs = cache_payload.get("jobs") or cache_payload.get("jobs_all") or []
    records = jobs_from_dicts(raw_jobs)
    filtered = filter_jobs_by_seniority(records, seniority_filter)
    by_source: dict[str, int] = {}
    for job in filtered:
        by_source[job.source] = by_source.get(job.source, 0) + 1
    out = dict(cache_payload)
    out["seniority_filter"] = seniority_filter or "any"
    out["count_before_seniority_filter"] = len(records)
    out["count"] = len(filtered)
    out["by_source"] = by_source
    out["jobs"] = [asdict(job) for job in filtered]
    out["refiltered_at"] = _now_iso()
    return out
