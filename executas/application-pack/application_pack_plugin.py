#!/usr/bin/env python3
"""application-pack — job link + tailored resume for manual apply (no email)."""
from __future__ import annotations

import json
import sys
from typing import Any

from pack_core import list_packs, prepare_all, prepare_one

MANIFEST = {
    "name": "application-pack",
    "display_name": "Application Pack",
    "version": "0.1.0",
    "description": (
        "Bundle passed jobs with tailored resume .tex paths for manual apply. "
        "Free-tier scrape (Indeed etc.) — open apply_url, upload Overleaf PDF, you submit."
    ),
    "author": "resumatch",
    "tools": [
        {
            "name": "application_pack",
            "description": "Prepare manual-apply packs from matched jobs + composed resumes.",
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: prepare_all, prepare, list",
                    "required": True,
                },
                {
                    "name": "job_index",
                    "type": "integer",
                    "description": "Passed job index (for prepare)",
                    "required": False,
                },
            ],
        }
    ],
}


def invoke(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    if tool != "application_pack":
        raise ValueError(f"unknown tool: {tool}")

    action = str(args.get("action", "")).strip().lower()

    if action == "prepare_all":
        return {"success": True, "data": prepare_all()}

    if action == "prepare":
        index = args.get("job_index")
        if index is None:
            raise ValueError("prepare requires job_index")
        return {"success": True, "data": prepare_one(int(index))}

    if action == "list":
        return {"success": True, "data": list_packs()}

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
