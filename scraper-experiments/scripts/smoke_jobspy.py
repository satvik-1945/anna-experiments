#!/usr/bin/env python3
"""Step-1 local scraper runner — thin CLI over executas/job-scraper/scraper_core.py."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "executas" / "job-scraper"))

from scraper_core import ScrapeConfig, parse_proxy_list, run_scrape, write_jobs_json  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local scraper experiments.")
    parser.add_argument("--mode", choices=["free", "boost"], default="free")
    parser.add_argument("--search-term", default="software engineer")
    parser.add_argument("--location", default="India")
    parser.add_argument("--hours-old", type=int, default=24)
    parser.add_argument("--results-wanted", type=int, default=200)
    parser.add_argument("--country-indeed", default="India")
    parser.add_argument(
        "--proxy",
        action="append",
        default=[],
        help="Proxy in host:port or user:pass@host:port format. Repeat for multiple.",
    )
    parser.add_argument(
        "--include-free-apis",
        action="store_true",
        help="Include Remotive/RemoteOK/Arbeitnow in the run.",
    )
    parser.add_argument(
        "--output",
        default="scraper-experiments/output/jobs_latest.json",
        help="Output JSON path.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "boost" and not args.proxy:
        print(
            "[warn] Boost mode enabled without proxies. LinkedIn may rate-limit quickly.",
        )

    config = ScrapeConfig(
        mode=args.mode,
        search_term=args.search_term,
        location=args.location,
        hours_old=args.hours_old,
        results_wanted=args.results_wanted,
        country_indeed=args.country_indeed,
        include_free_apis=args.include_free_apis,
        proxies=args.proxy or parse_proxy_list(__import__("os").environ.get("SCRAPER_PROXY_LIST")),
    )

    print("[info] Running scrape...")
    result = run_scrape(config)

    from scraper_core import JobRecord

    jobs = [JobRecord(**j) for j in result["jobs"]]
    write_jobs_json(Path(args.output), jobs)

    print(f"[done] Wrote {result['count']} unique jobs to {args.output}")
    print(f"[done] Source split: {json.dumps(result['by_source'], indent=2)}")
    if result["api_errors"]:
        print(f"[warn] API errors: {result['api_errors']}")


if __name__ == "__main__":
    main()
