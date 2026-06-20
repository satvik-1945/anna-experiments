#!/usr/bin/env python3
"""job-matcher — score scraped jobs against ResuMatch profile."""
from __future__ import annotations

import json
import sys
from typing import Any

from matcher_core import DEFAULT_MATCH_PATH, run_match

MANIFEST = {
    "name": "job-matcher",
    "display_name": "Job Matcher",
    "version": "0.1.0",
    "description": (
        "Score job listings against your saved profile. "
        "Jobs at or above threshold (default 80%) are marked passed for tailoring."
    ),
    "author": "resumatch",
    "tools": [
        {
            "name": "job_matcher",
            "description": "Score jobs from jobs_latest.json vs profile; return passed/rejected lists.",
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: score, passed, summary",
                    "required": True,
                },
                {
                    "name": "threshold",
                    "type": "number",
                    "description": "Pass threshold 0-100 (default 80)",
                    "required": False,
                },
                {
                    "name": "jobs_path",
                    "type": "string",
                    "description": "Optional path to jobs JSON (default ~/.anna/resumatch/jobs_latest.json)",
                    "required": False,
                },
                {
                    "name": "ensure_passed",
                    "type": "integer",
                    "description": "If none meet threshold, include up to N top-scored jobs for manual review",
                    "required": False,
                },
            ],
        }
    ],
}

_LAST_MATCH: dict[str, Any] | None = None


def invoke(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    global _LAST_MATCH

    if tool != "job_matcher":
        raise ValueError(f"unknown tool: {tool}")

    action = str(args.get("action", "")).strip().lower()

    if action == "score":
        threshold = float(args.get("threshold") or 80)
        ensure_passed = int(args.get("ensure_passed") or 0)
        result = run_match(
            threshold=threshold,
            jobs_path=args.get("jobs_path"),
            save=True,
            ensure_passed=ensure_passed,
        )
        _LAST_MATCH = result
        return {"success": True, "data": result}

    if action == "passed":
        if _LAST_MATCH is None:
            path = DEFAULT_MATCH_PATH
            if path.exists():
                _LAST_MATCH = json.loads(path.read_text(encoding="utf-8"))
            else:
                return {
                    "success": True,
                    "data": {
                        "message": "No match results yet. Run action score first.",
                        "passed_count": 0,
                        "passed": [],
                    },
                }
        passed = _LAST_MATCH.get("passed") or []
        preview = [
            {
                "title": item["job"].get("title"),
                "company": item["job"].get("company"),
                "score": item.get("score"),
                "apply_url": item["job"].get("apply_url"),
            }
            for item in passed[:20]
        ]
        return {
            "success": True,
            "data": {
                "passed_count": len(passed),
                "threshold": _LAST_MATCH.get("threshold"),
                "preview": preview,
            },
        }

    if action == "summary":
        if _LAST_MATCH is None and DEFAULT_MATCH_PATH.exists():
            data = json.loads(DEFAULT_MATCH_PATH.read_text(encoding="utf-8"))
        elif _LAST_MATCH is not None:
            data = _LAST_MATCH
        else:
            return {
                "success": True,
                "data": {"message": "No match run yet."},
            }
        return {
            "success": True,
            "data": {
                "total": data.get("total", 0),
                "passed_count": data.get("passed_count", 0),
                "rejected_count": data.get("rejected_count", 0),
                "threshold": data.get("threshold"),
                "scored_at": data.get("scored_at"),
                "saved_to": data.get("saved_to"),
            },
        }

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
