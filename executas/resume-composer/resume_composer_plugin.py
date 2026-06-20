#!/usr/bin/env python3
"""resume-composer — tailor LaTeX Skills section per passed job."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from composer_core import (
    DEFAULT_OUTPUT_DIR,
    compose_all,
    compose_by_index,
    compose_for_job,
    compile_pdf,
    load_passed_jobs,
)

MANIFEST = {
    "name": "resume-composer",
    "display_name": "Resume Composer",
    "version": "0.1.0",
    "description": (
        "Tailor the Skills section of your Overleaf LaTeX resume per job description. "
        "Only reorders/highlights skills already in your resume — ATS-friendly, no fabrication."
    ),
    "author": "resumatch",
    "tools": [
        {
            "name": "resume_composer",
            "description": "Generate job-specific .tex files by tailoring the Skills section.",
            "timeout": 180,
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: compose, compose_all, compile_pdf, list",
                    "required": True,
                },
                {
                    "name": "job_index",
                    "type": "integer",
                    "description": "Index into passed jobs from match_results (for compose / compile_pdf)",
                    "required": False,
                },
                {
                    "name": "tex_path",
                    "type": "string",
                    "description": "Optional path to a .tex file (for compile_pdf)",
                    "required": False,
                },
            ],
        }
    ],
}


def invoke(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    if tool != "resume_composer":
        raise ValueError(f"unknown tool: {tool}")

    action = str(args.get("action", "")).strip().lower()

    if action == "compose":
        index = args.get("job_index")
        if index is None:
            raise ValueError("compose requires job_index (0 = top passed job)")
        result = compose_by_index(int(index))
        return {"success": True, "data": result}

    if action == "compose_all":
        result = compose_all()
        return {"success": True, "data": result}

    if action == "compile_pdf":
        index = args.get("job_index")
        tex_path = args.get("tex_path")
        if index is None and not tex_path:
            raise ValueError("compile_pdf requires job_index or tex_path")
        result = compile_pdf(
            job_index=int(index) if index is not None else None,
            tex_path=str(tex_path) if tex_path else None,
        )
        return {"success": True, "data": result}

    if action == "list":
        out_dir = Path(DEFAULT_OUTPUT_DIR)
        if not out_dir.exists():
            return {"success": True, "data": {"files": [], "message": "No composed resumes yet."}}
        files = sorted(str(p) for p in out_dir.glob("resume_*.tex"))
        manifest = out_dir / "manifest.json"
        return {
            "success": True,
            "data": {
                "files": files,
                "manifest_path": str(manifest) if manifest.exists() else None,
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
