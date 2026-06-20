#!/usr/bin/env python3
"""profile — ResuMatch Anna Executa for user job-search profile (local JSON, APS-ready)."""
from __future__ import annotations

import json
import sys
from typing import Any

from profile_core import (
    JOB_DOMAINS,
    SENIORITY_LEVELS,
    build_profile,
    load_profile,
    profile_for_scraper,
    profile_is_complete,
    profile_path,
    resume_tex_path,
    save_profile,
)

MANIFEST = {
    "name": "resumatch-profile",
    "display_name": "ResuMatch Profile",
    "version": "0.1.0",
    "description": (
        "Create and store a job-search profile: domain, seniority, experience, location, "
        "plus Overleaf LaTeX resume. Saved at ~/.anna/resumatch/ "
        "(single-user, no login — your machine is the account)."
    ),
    "author": "resumatch",
    "host_capabilities": ["storage.tool"],
    "tools": [
        {
            "name": "user_profile",
            "description": "Save, read, or build a job-search profile from resume + preferences.",
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: save, get, domains, scraper_defaults",
                    "required": True,
                },
                {
                    "name": "domain",
                    "type": "string",
                    "description": f"Job domain key, e.g. software_engineering. Options: {', '.join(JOB_DOMAINS)}",
                    "required": False,
                },
                {
                    "name": "seniority",
                    "type": "string",
                    "description": f"One of: {', '.join(SENIORITY_LEVELS)}",
                    "required": False,
                },
                {
                    "name": "years_experience",
                    "type": "integer",
                    "description": "Total years of relevant experience",
                    "required": False,
                },
                {
                    "name": "location",
                    "type": "string",
                    "description": "Preferred job location, e.g. India, Remote",
                    "required": False,
                },
                {
                    "name": "search_term",
                    "type": "string",
                    "description": "Job titles/keywords to search Indeed, e.g. Python FastAPI developer",
                    "required": False,
                },
                {
                    "name": "target_skills",
                    "type": "string",
                    "description": "Comma-separated skills that must appear in job posts, e.g. python, fastapi, aws",
                    "required": False,
                },
                {
                    "name": "resume_latex",
                    "type": "string",
                    "description": "Paste full Overleaf LaTeX source (.tex) — preferred over plain text",
                    "required": False,
                },
                {
                    "name": "resume_tex_path",
                    "type": "string",
                    "description": "Optional path to resume .tex file on this machine",
                    "required": False,
                },
                {
                    "name": "resume_text",
                    "type": "string",
                    "description": "Fallback: plain text resume if LaTeX not available",
                    "required": False,
                },
                {
                    "name": "name",
                    "type": "string",
                    "description": "Optional name override",
                    "required": False,
                },
                {
                    "name": "email",
                    "type": "string",
                    "description": "Optional email override",
                    "required": False,
                },
                {
                    "name": "phone",
                    "type": "string",
                    "description": "Optional phone override",
                    "required": False,
                },
            ],
        }
    ],
}


def invoke(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    if tool != "user_profile":
        raise ValueError(f"unknown tool: {tool}")

    action = str(args.get("action", "")).strip().lower()

    if action == "domains":
        return {
            "success": True,
            "data": {
                "domains": JOB_DOMAINS,
                "seniority_levels": list(SENIORITY_LEVELS),
            },
        }

    if action == "get":
        profile = load_profile()
        if profile is None:
            return {
                "success": True,
                "data": {
                    "exists": False,
                    "path": str(profile_path()),
                    "message": "No profile yet. Paste Overleaf LaTeX (resume_latex) + domain, seniority, years_experience, location.",
                },
            }
        data = profile.to_dict()
        data["effective_search_term"] = profile.effective_search_term()
        data["scrape_search_term"] = profile.scrape_search_term()
        data["exists"] = True
        data["profile_complete"] = profile_is_complete(profile)
        data["path"] = str(profile_path())
        return {"success": True, "data": data}

    if action == "scraper_defaults":
        defaults = profile_for_scraper()
        if not defaults:
            return {
                "success": True,
                "data": {
                    "profile_loaded": False,
                    "message": "No profile saved — scraper will use its own defaults.",
                },
            }
        return {"success": True, "data": defaults}

    if action == "save":
        required = ("domain", "seniority", "years_experience", "location")
        missing = [key for key in required if args.get(key) in (None, "")]
        if missing:
            raise ValueError(f"save requires: {', '.join(missing)}")

        if not (
            args.get("resume_latex")
            or args.get("resume_tex_path")
            or args.get("resume_text")
            or args.get("resume_path")
        ):
            raise ValueError("save requires resume_latex (Overleaf paste), resume_tex_path, or resume_text")

        profile = build_profile(
            domain=str(args["domain"]),
            seniority=str(args["seniority"]),
            years_experience=int(args["years_experience"]),
            location=str(args["location"]),
            resume_text=str(args.get("resume_text") or ""),
            resume_latex=str(args.get("resume_latex") or ""),
            resume_path=str(args.get("resume_path") or ""),
            resume_tex_path_arg=str(args.get("resume_tex_path") or ""),
            search_term=str(args.get("search_term") or ""),
            target_skills=args.get("target_skills"),
            name=str(args.get("name") or ""),
            email=str(args.get("email") or ""),
            phone=str(args.get("phone") or ""),
        )
        path = save_profile(profile)
        data = profile.to_dict()
        data["effective_search_term"] = profile.effective_search_term()
        data["scrape_search_term"] = profile.scrape_search_term()
        data["exists"] = True
        data["profile_complete"] = profile_is_complete(profile)
        data["saved_to"] = str(path)
        data["resume_tex_saved_to"] = str(resume_tex_path()) if profile.resume_tex else None
        return {"success": True, "data": data}

    raise ValueError(f"unknown action: {action}")


def handle(req: dict[str, Any]) -> dict[str, Any]:
    method = req.get("method")
    if method == "describe":
        return {"result": MANIFEST}
    if method == "invoke":
        params = req.get("params") or {}
        try:
            return {"result": invoke(params.get("tool", ""), params.get("arguments") or {})}
        except ValueError as exc:
            return {"error": {"code": -32601, "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            print(f"invoke error: {exc}", file=sys.stderr)
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
