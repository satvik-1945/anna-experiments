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
                    "description": "One of: scrape, summary",
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
                    "description": "Only jobs posted within this many hours (default 24)",
                    "required": False,
                },
                {
                    "name": "results_wanted",
                    "type": "integer",
                    "description": "Maximum jobs to fetch (default 200)",
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
                    "description": "Save full scrape to ~/.anna/resumatch/jobs_latest.json for job_matcher (default true)",
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

    scrape_notes: list[str] = []
    if os.environ.get("RESUMATCH_SMOKE_MOCK") == "1":
        full = _mock_scrape_result()
    else:
        from scraper_core import ScrapeConfig, run_scrape

        config = ScrapeConfig(
            mode=str(args.get("mode", "free")),
            search_term=str(args.get("search_term", "software engineer")),
            location=str(args.get("location", "India")),
            hours_old=int(args.get("hours_old", 24)),
            results_wanted=int(args.get("results_wanted", 200)),
            country_indeed=str(args.get("country_indeed", "India")),
            include_free_apis=bool(args.get("include_free_apis", False)),
            proxies=_resolve_proxies(args, credentials),
        )
        full = run_scrape(config)
        if full["count"] == 0 and config.hours_old < 72:
            config = ScrapeConfig(
                mode=config.mode,
                search_term=config.search_term,
                location=config.location,
                hours_old=72,
                results_wanted=config.results_wanted,
                country_indeed=config.country_indeed,
                include_free_apis=config.include_free_apis,
                proxies=config.proxies,
            )
            full = run_scrape(config)
            scrape_notes.append("retried hours_old=72")
        if full["count"] == 0:
            words = config.search_term.split()
            if len(words) > 2:
                short = " ".join(words[:2])
                config = ScrapeConfig(
                    mode=config.mode,
                    search_term=short,
                    location=config.location,
                    hours_old=max(config.hours_old, 72),
                    results_wanted=config.results_wanted,
                    country_indeed=config.country_indeed,
                    include_free_apis=config.include_free_apis,
                    proxies=config.proxies,
                )
                full = run_scrape(config)
                scrape_notes.append(f"retried query={short!r}")

    _LAST_SCRAPE = full

    response_extra: dict[str, str] = {}
    persist = args.get("persist", True)
    if persist is not False:
        default_jobs = Path.home() / ".anna" / "resumatch" / "jobs_latest.json"
        env_jobs = os.environ.get("RESUMATCH_JOBS_PATH", "").strip()
        jobs_path = Path(env_jobs) if env_jobs else default_jobs
        jobs_path.parent.mkdir(parents=True, exist_ok=True)
        jobs_path.write_text(json.dumps(full, indent=2), encoding="utf-8")
        response_extra["jobs_saved_to"] = str(jobs_path)

    output_path = args.get("output_path")
    if output_path:
        path = Path(str(output_path))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(full["jobs"], indent=2), encoding="utf-8")
        response_extra["output_path"] = str(path)

    max_chars = int(args.get("description_max_chars", 400))
    max_response_jobs = int(args.get("max_response_jobs", 10))
    response = dict(full)
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
    if action == "summary":
        return {"success": True, "data": summary_action()}
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
