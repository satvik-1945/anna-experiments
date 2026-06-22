#!/usr/bin/env python3
"""job-scraper — ResuMatch Anna Executa plugin for collecting fresh job listings."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

MANIFEST = {
    "name": "job-scraper",
    "display_name": "Job Scraper",
    "version": "0.1.0",
    "description": (
        "Scrape recent job listings from Indeed, Google Jobs, and optional free APIs. "
        "Use free mode by default; boost mode adds LinkedIn (proxies recommended)."
    ),
    "author": "resumatch",
    "credentials": [
        {
            "name": "SCRAPER_PROXY_LIST",
            "display_name": "Scraper proxy list",
            "description": (
                "Optional comma-separated proxies for LinkedIn boost mode "
                "(user:pass@host:port or host:port)."
            ),
            "required": False,
            "sensitive": True,
        }
    ],
    "tools": [
        {
            "name": "job_scraper",
            "description": "Scrape jobs from the last N hours or return the last scrape summary.",
            "timeout": 300,
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: scrape, refilter, cache_status, summary, get_job",
                    "required": True,
                },
                {
                    "name": "use_profile",
                    "type": "boolean",
                    "description": "Load search_term and location from saved ResuMatch profile (~/.anna/resumatch/profile.json)",
                    "required": False,
                },
                {
                    "name": "mode",
                    "type": "string",
                    "description": "free (default) or boost (includes LinkedIn)",
                    "required": False,
                },
                {
                    "name": "search_term",
                    "type": "string",
                    "description": "Job search keywords, e.g. software engineer",
                    "required": False,
                },
                {
                    "name": "location",
                    "type": "string",
                    "description": "Location filter, e.g. India",
                    "required": False,
                },
                {
                    "name": "hours_old",
                    "type": "integer",
                    "description": "Only jobs posted within this many hours (default 168 = 7 days)",
                    "required": False,
                },
                {
                    "name": "seniority_filter",
                    "type": "string",
                    "description": "Filter scraped jobs by level: any, intern, junior, mid, senior",
                    "required": False,
                },
                {
                    "name": "results_wanted",
                    "type": "integer",
                    "description": "Maximum jobs to fetch from Indeed/Google (default 500)",
                    "required": False,
                },
                {
                    "name": "country_indeed",
                    "type": "string",
                    "description": "Indeed/Glassdoor country name (default India)",
                    "required": False,
                },
                {
                    "name": "include_free_apis",
                    "type": "boolean",
                    "description": "Also query Remotive, RemoteOK, Arbeitnow",
                    "required": False,
                },
                {
                    "name": "proxies",
                    "type": "array",
                    "description": "Optional proxy list; overrides SCRAPER_PROXY_LIST credential",
                    "required": False,
                },
                {
                    "name": "persist",
                    "type": "boolean",
                    "description": "Save full scrape to ~/.anna/resumatch/jobs_latest.json (default true)",
                    "required": False,
                },
                {
                    "name": "output_path",
                    "type": "string",
                    "description": "Optional path to write full job JSON (descriptions not truncated)",
                    "required": False,
                },
                {
                    "name": "description_max_chars",
                    "type": "integer",
                    "description": "Truncate descriptions in the tool response (default 400)",
                    "required": False,
                },
            ],
        }
    ],
}

_LAST_SCRAPE: dict[str, Any] | None = None


def _jobs_dir() -> Path:
    return Path.home() / ".anna" / "resumatch"


def _cache_path() -> Path:
    env = os.environ.get("RESUMATCH_JOBS_CACHE_PATH", "").strip()
    return Path(env) if env else _jobs_dir() / "jobs_cache.json"


def _latest_path() -> Path:
    env = os.environ.get("RESUMATCH_JOBS_PATH", "").strip()
    return Path(env) if env else _jobs_dir() / "jobs_latest.json"


def _persist_scrape(full: dict[str, Any]) -> dict[str, str]:
    latest_path = _latest_path()
    cache_path = _cache_path()
    latest_path.parent.mkdir(parents=True, exist_ok=True)

    cache_payload = dict(full)
    cache_payload["jobs"] = full.get("jobs_all") or full.get("jobs") or []
    cache_payload.pop("jobs_all", None)
    cache_path.write_text(json.dumps(cache_payload, indent=2), encoding="utf-8")

    latest_payload = dict(full)
    latest_payload.pop("jobs_all", None)
    latest_path.write_text(json.dumps(latest_payload, indent=2), encoding="utf-8")

    return {
        "jobs_saved_to": str(latest_path),
        "jobs_cache_saved_to": str(cache_path),
    }


def refilter_jobs_action(args: dict[str, Any]) -> dict[str, Any]:
    global _LAST_SCRAPE

    cache_path = _cache_path()
    if not cache_path.exists():
        raise ValueError("No job cache yet. Click Fetch jobs first (one-time scrape).")

    from scraper_core import refilter_cached_jobs

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    seniority = str(args.get("seniority_filter", "any")).strip().lower()
    full = refilter_cached_jobs(cache, seniority)
    latest_path = _latest_path()
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_payload = dict(full)
    latest_payload.pop("jobs_all", None)
    latest_path.write_text(json.dumps(latest_payload, indent=2), encoding="utf-8")

    _LAST_SCRAPE = full

    max_chars = int(args.get("description_max_chars", 400))
    max_response_jobs = int(args.get("max_response_jobs", 10))
    response = dict(full)
    response.pop("jobs_all", None)
    response["jobs"] = _truncate_jobs(full["jobs"], max_chars)[:max_response_jobs]
    response["jobs_in_response"] = len(response["jobs"])
    response["jobs_preview_only"] = response["jobs_in_response"] < full["count"]
    response["from_cache"] = True
    response["jobs_saved_to"] = str(latest_path)
    response["jobs_cache_saved_to"] = str(cache_path)
    return response


def cache_status_action() -> dict[str, Any]:
    cache_path = _cache_path()
    latest_path = _latest_path()
    out: dict[str, Any] = {
        "cache_exists": cache_path.exists(),
        "latest_exists": latest_path.exists(),
        "cache_path": str(cache_path),
        "latest_path": str(latest_path),
    }
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            out["cached_count"] = len(cache.get("jobs") or [])
            out["fetched_at"] = cache.get("fetched_at")
            out["search_term"] = cache.get("search_term")
            out["hours_old"] = cache.get("hours_old")
        except (json.JSONDecodeError, OSError):
            out["cache_error"] = "Could not read jobs_cache.json"
    if latest_path.exists():
        try:
            latest = json.loads(latest_path.read_text(encoding="utf-8"))
            out["filtered_count"] = latest.get("count")
            out["count_before_seniority_filter"] = latest.get("count_before_seniority_filter")
            out["seniority_filter"] = latest.get("seniority_filter")
            out["refiltered_at"] = latest.get("refiltered_at")
        except (json.JSONDecodeError, OSError):
            out["latest_error"] = "Could not read jobs_latest.json"
    return out


def get_job_action(args: dict[str, Any]) -> dict[str, Any]:
    """Return a single job (title/company/description) by its index in the
    latest fetch — small payload so the UI can pass the JD to the LLM without
    shipping every description across RPC."""
    index = args.get("job_index")
    if index is None:
        raise ValueError("get_job requires job_index")
    index = int(index)
    latest_path = _latest_path()
    if not latest_path.exists():
        raise ValueError("No jobs yet. Click Fetch jobs first.")
    try:
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("Could not read jobs_latest.json") from exc
    jobs = list(latest.get("jobs") or [])
    if index < 0 or index >= len(jobs):
        raise ValueError(f"job_index out of range (0..{len(jobs) - 1})")
    job = jobs[index]
    desc = str(job.get("description") or "")
    max_chars = int(args.get("description_max_chars", 6000))
    if max_chars and len(desc) > max_chars:
        desc = desc[:max_chars]
    return {
        "job_index": index,
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "description": desc,
    }


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _mock_scrape_result() -> dict[str, Any]:
    return {
        "mode": "free",
        "search_term": "software engineer",
        "location": "India",
        "hours_old": 24,
        "count": 1,
        "by_source": {"mock": 1},
        "apply_url_coverage": 100.0,
        "api_errors": [],
        "linkedin_included": False,
        "fetched_at": "2026-06-18T00:00:00+00:00",
        "jobs": [
            {
                "source": "mock",
                "source_type": "board",
                "title": "Mock Software Engineer",
                "company": "Mock Co",
                "location": "Remote",
                "published_at": "2026-06-18",
                "apply_url": "https://example.com/jobs/1",
                "description": "A" * 120,
                "tags": [],
                "fetched_at": "2026-06-18T00:00:00+00:00",
            }
        ],
    }


def _truncate_jobs(jobs: list[dict[str, Any]], max_chars: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for job in jobs:
        copy = dict(job)
        desc = copy.get("description") or ""
        if len(desc) > max_chars:
            copy["description"] = desc[: max_chars - 1] + "…"
        out.append(copy)
    return out


def _resolve_proxies(args: dict[str, Any], credentials: dict[str, str] | None) -> list[str]:
    from scraper_core import parse_proxy_list

    from_args = args.get("proxies")
    if isinstance(from_args, list) and from_args:
        return [str(p).strip() for p in from_args if str(p).strip()]

    creds = credentials or {}
    from_creds = parse_proxy_list(creds.get("SCRAPER_PROXY_LIST"))
    if from_creds:
        return from_creds

    return parse_proxy_list(os.environ.get("SCRAPER_PROXY_LIST"))


def _normalize_search(query: str, max_words: int = 4) -> str:
    q = str(query or "").strip()
    if not q:
        return q
    if "," in q:
        q = q.split(",")[0].strip()
    words = q.split()
    if len(words) > max_words:
        q = " ".join(words[:max_words])
    return q


def _load_profile_defaults() -> dict[str, Any]:
    """Read shared profile JSON written by resumatch-profile executa."""
    env_path = os.environ.get("RESUMATCH_PROFILE_PATH", "").strip()
    path = Path(env_path) if env_path else Path.home() / ".anna" / "resumatch" / "profile.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        data = raw.get("profile") or raw
        search = (data.get("search_term") or "").strip()
        if not search:
            domain = data.get("domain", "software_engineering")
            domain_terms = {
                "software_engineering": "software engineer",
                "data_science": "data scientist",
                "machine_learning": "machine learning engineer",
                "accounting": "accountant",
                "taxation": "tax analyst",
                "banking": "banking officer",
                "teaching": "teacher",
            }
            base = domain_terms.get(domain, "professional")
            seniority = data.get("seniority", "mid")
            if seniority in ("senior", "lead", "manager", "director"):
                search = f"senior {base}"
            elif seniority == "junior":
                search = f"junior {base}"
            elif seniority == "intern":
                search = f"intern {base}"
            else:
                search = base
        search_full = search
        search = _normalize_search(search)
        return {
            "search_term": search,
            "search_term_full": search_full,
            "location": data.get("location") or "India",
            "profile_domain": data.get("domain"),
            "profile_seniority": data.get("seniority"),
        }
    except (json.JSONDecodeError, OSError) as exc:
        _log(f"profile read warning: {exc}")
        return {}


def _merge_profile_args(args: dict[str, Any]) -> dict[str, Any]:
    merged = dict(args)
    use_profile = merged.get("use_profile")
    if use_profile is False and merged.get("search_term") and merged.get("location"):
        return merged
    if use_profile is not False and not merged.get("search_term") and not merged.get("location"):
        use_profile = True
    if not use_profile:
        return merged
    defaults = _load_profile_defaults()
    if not defaults:
        return merged
    merged.setdefault("search_term", defaults["search_term"])
    merged.setdefault("location", defaults["location"])
    merged["_profile_applied"] = True
    merged["_profile_domain"] = defaults.get("profile_domain")
    merged["_profile_search_full"] = defaults.get("search_term_full")
    return merged


def scrape_jobs_action(
    args: dict[str, Any],
    credentials: dict[str, str] | None,
) -> dict[str, Any]:
    global _LAST_SCRAPE

    args = _merge_profile_args(args)
    seniority_filter = str(args.get("seniority_filter") or "any").strip().lower()

    scrape_notes: list[str] = []
    if os.environ.get("RESUMATCH_SMOKE_MOCK") == "1":
        full = _mock_scrape_result()
    else:
        from scraper_core import ScrapeConfig, run_scrape

        def _do_scrape(cfg: ScrapeConfig) -> dict[str, Any]:
            return run_scrape(cfg, seniority_filter=seniority_filter)

        config = ScrapeConfig(
            mode=str(args.get("mode", "free")),
            search_term=str(args.get("search_term", "software engineer")),
            location=str(args.get("location", "India")),
            hours_old=int(args.get("hours_old", 168)),
            results_wanted=int(args.get("results_wanted", 500)),
            country_indeed=str(args.get("country_indeed", "India")),
            include_free_apis=bool(args.get("include_free_apis", True)),
            proxies=_resolve_proxies(args, credentials),
        )
        full = _do_scrape(config)
        if full["count"] == 0 and config.hours_old < 168:
            config = ScrapeConfig(
                mode=config.mode,
                search_term=config.search_term,
                location=config.location,
                hours_old=168,
                results_wanted=config.results_wanted,
                country_indeed=config.country_indeed,
                include_free_apis=config.include_free_apis,
                proxies=config.proxies,
            )
            full = _do_scrape(config)
            scrape_notes.append("retried hours_old=168")
        if full["count"] == 0 and config.hours_old < 336:
            config = ScrapeConfig(
                mode=config.mode,
                search_term=config.search_term,
                location=config.location,
                hours_old=336,
                results_wanted=config.results_wanted,
                country_indeed=config.country_indeed,
                include_free_apis=config.include_free_apis,
                proxies=config.proxies,
            )
            full = _do_scrape(config)
            scrape_notes.append("retried hours_old=336")
        if full["count"] == 0:
            words = config.search_term.split()
            if len(words) > 2:
                short = " ".join(words[:2])
                config = ScrapeConfig(
                    mode=config.mode,
                    search_term=short,
                    location=config.location,
                    hours_old=max(config.hours_old, 168),
                    results_wanted=config.results_wanted,
                    country_indeed=config.country_indeed,
                    include_free_apis=config.include_free_apis,
                    proxies=config.proxies,
                )
                full = _do_scrape(config)
                scrape_notes.append(f"retried query={short!r}")

    _LAST_SCRAPE = full

    response_extra: dict[str, str] = {}
    persist = args.get("persist", True)
    if persist is not False:
        response_extra.update(_persist_scrape(full))

    output_path = args.get("output_path")
    if output_path:
        path = Path(str(output_path))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(full["jobs"], indent=2), encoding="utf-8")
        response_extra["output_path"] = str(path)

    max_chars = int(args.get("description_max_chars", 400))
    max_response_jobs = int(args.get("max_response_jobs", 10))
    response = dict(full)
    response.pop("jobs_all", None)
    preview_source = _truncate_jobs(full["jobs"], max_chars)
    response["jobs"] = preview_source[:max_response_jobs]
    response["jobs_in_response"] = len(response["jobs"])
    response["jobs_preview_only"] = response["jobs_in_response"] < full["count"]
    if args.get("_profile_applied"):
        response["profile_applied"] = True
        response["profile_domain"] = args.get("_profile_domain")
        if args.get("_profile_search_full"):
            response["search_term_full"] = args.get("_profile_search_full")
    if scrape_notes:
        response["scrape_notes"] = scrape_notes
    if full["count"] == 0:
        response["warning"] = (
            "Indeed returned 0 jobs. Try a shorter search in Profile "
            '(e.g. "Python developer" not a long list of titles).'
        )
    response.update(response_extra)
    return response


def summary_action() -> dict[str, Any]:
    if _LAST_SCRAPE is None:
        return {
            "count": 0,
            "message": "No scrape has run in this plugin session yet.",
        }

    jobs = _LAST_SCRAPE.get("jobs") or []
    preview = [
        {
            "title": j.get("title"),
            "company": j.get("company"),
            "location": j.get("location"),
            "apply_url": j.get("apply_url"),
            "source": j.get("source"),
        }
        for j in jobs[:10]
    ]
    return {
        "count": _LAST_SCRAPE.get("count", 0),
        "by_source": _LAST_SCRAPE.get("by_source", {}),
        "fetched_at": _LAST_SCRAPE.get("fetched_at"),
        "search_term": _LAST_SCRAPE.get("search_term"),
        "location": _LAST_SCRAPE.get("location"),
        "preview": preview,
    }


def invoke(
    tool: str,
    args: dict[str, Any],
    credentials: dict[str, str] | None = None,
) -> dict[str, Any]:
    if tool != "job_scraper":
        raise ValueError(f"unknown tool: {tool}")

    action = str(args.get("action", "")).strip().lower()
    if action == "scrape":
        return {"success": True, "data": scrape_jobs_action(args, credentials)}
    if action == "refilter":
        return {"success": True, "data": refilter_jobs_action(args)}
    if action == "cache_status":
        return {"success": True, "data": cache_status_action()}
    if action == "summary":
        return {"success": True, "data": summary_action()}
    if action == "get_job":
        return {"success": True, "data": get_job_action(args)}
    raise ValueError(f"unknown action: {action}")


def handle(req: dict[str, Any]) -> dict[str, Any]:
    method = req.get("method")
    if method == "describe":
        return {"result": MANIFEST}
    if method == "invoke":
        params = req.get("params") or {}
        context = params.get("context") or {}
        credentials = context.get("credentials") if isinstance(context, dict) else None
        try:
            return {
                "result": invoke(
                    params.get("tool", ""),
                    params.get("arguments") or {},
                    credentials,
                )
            }
        except ValueError as exc:
            return {"error": {"code": -32601, "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            _log(f"invoke error: {exc}")
            return {"error": {"code": -32603, "message": str(exc)}}
    if method == "health":
        return {"result": {"status": "ready"}}
    return {"error": {"code": -32601, "message": f"unknown method: {method}"}}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            payload = {"error": {"code": -32700, "message": str(exc)}}
            req_id = None
        else:
            payload = handle(req)
            req_id = req.get("id")
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, **payload}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
