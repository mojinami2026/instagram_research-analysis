"""Weekly Instagram viral video research using Brave Search API (free tier)."""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

from config import (
    PERSONAL_BRAND_NICHES,
    REPORT_OUTPUT_DIR,
    RESEARCH_QUERIES,
)

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def brave_search(query: str, api_key: str, count: int = 10) -> list[dict]:
    """Call Brave Search API and return a list of results."""
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "freshness": "pw",  # past week
        "text_decorations": False,
        "search_lang": "en",
        "country": "us",
    }

    response = requests.get(BRAVE_SEARCH_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("web", {}).get("results", []):
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "age": item.get("age", ""),
            }
        )
    return results


def run_research(api_key: str) -> list[dict]:
    """Run Brave searches for all research queries."""
    findings = []

    print(f"Running {len(RESEARCH_QUERIES)} research queries via Brave Search...")

    for i, query in enumerate(RESEARCH_QUERIES, 1):
        print(f"  [{i}/{len(RESEARCH_QUERIES)}] Searching: {query}")
        try:
            results = brave_search(query, api_key)
            findings.append(
                {
                    "query": query,
                    "results": results,
                    "result_count": len(results),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except requests.HTTPError as e:
            print(f"    Warning: search failed ({e}), skipping.")
            findings.append(
                {
                    "query": query,
                    "results": [],
                    "result_count": 0,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        # Brave free tier: 1 request/second
        if i < len(RESEARCH_QUERIES):
            time.sleep(1)

    return findings


def format_results_section(finding: dict) -> str:
    """Format a single query's results as a markdown section."""
    lines = [f"### Query: {finding['query']}\n"]

    if not finding["results"]:
        lines.append("_No results found or search failed._\n")
        return "\n".join(lines)

    for j, r in enumerate(finding["results"], 1):
        age = f" _(published: {r['age']})_" if r.get("age") else ""
        lines.append(f"**{j}. {r['title']}**{age}")
        if r.get("description"):
            lines.append(f"> {r['description']}")
        lines.append(f"- {r['url']}")
        lines.append("")

    return "\n".join(lines)


def build_report(findings: list[dict], week_start: str, week_end: str) -> str:
    """Build the full weekly markdown report from findings."""
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total_results = sum(f["result_count"] for f in findings)

    lines = [
        f"# Instagram Viral Video Research — Week of {week_start}",
        "",
        f"_Generated: {generated_at} | Period: {week_start} → {week_end} | Total results: {total_results}_",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"This report aggregates **{total_results} search results** across **{len(findings)} queries** "
        f"targeting viral Instagram content in personal brand niches.",
        "",
        "**Niches covered:**",
    ]

    for niche in PERSONAL_BRAND_NICHES:
        lines.append(f"- {niche}")

    lines += [
        "",
        "---",
        "",
        "## Search Results by Query",
        "",
    ]

    for finding in findings:
        lines.append(format_results_section(finding))
        lines.append("---")
        lines.append("")

    lines += [
        "## How to Use This Report",
        "",
        "1. **Review titles and descriptions** — look for recurring themes, formats, and hooks",
        "2. **Visit the top URLs** — watch or read the content to study what made it viral",
        "3. **Note patterns** — which niches appear most? What words recur in titles?",
        "4. **Extract hooks** — copy exact phrasing from high-performing headlines as inspiration",
        "5. **Create your content** — model your next Reel's structure on 2-3 viral examples",
        "",
        "_Re-run this script each Monday to get a fresh weekly snapshot._",
    ]

    return "\n".join(lines)


def save_outputs(findings: list[dict], report: str, week_start: str) -> tuple[str, str]:
    """Save raw JSON findings and the markdown report."""
    output_dir = Path(REPORT_OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    date_slug = week_start.replace("-", "")

    json_path = output_dir / f"findings_{date_slug}.json"
    json_path.write_text(
        json.dumps(
            {
                "week_start": week_start,
                "generated_at": datetime.utcnow().isoformat(),
                "niches_researched": PERSONAL_BRAND_NICHES,
                "queries": RESEARCH_QUERIES,
                "findings": findings,
            },
            indent=2,
        )
    )

    md_path = output_dir / f"weekly_report_{date_slug}.md"
    md_path.write_text(report)

    return str(json_path), str(md_path)


def main():
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        print("Error: BRAVE_API_KEY environment variable not set.", file=sys.stderr)
        print("Get a free key at: https://brave.com/search/api/", file=sys.stderr)
        sys.exit(1)

    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_start_str = str(week_start)
    week_end_str = str(week_end)

    print(f"\n=== Instagram Viral Research: Week of {week_start_str} ===\n")

    findings = run_research(api_key)
    report = build_report(findings, week_start_str, week_end_str)
    json_path, md_path = save_outputs(findings, report, week_start_str)

    print(f"\n=== Research Complete ===")
    print(f"Raw findings : {json_path}")
    print(f"Weekly report: {md_path}")


if __name__ == "__main__":
    main()
