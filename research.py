"""Weekly Instagram content research using DuckDuckGo (no API key required).

Runs two tracks:
  1. Viral content research — study hooks/formats in the account's niches.
  2. Hot-take research — trending news & culture topics to react to with an
     opinionated "angry breakdown" commentary style.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from duckduckgo_search import DDGS

from config import (
    HOT_TAKE_ANGLES,
    HOT_TAKE_QUERIES,
    NICHES,
    REPORT_OUTPUT_DIR,
    VIRAL_QUERIES,
)


def ddg_search(query: str, max_results: int = 10, timelimit: str = "m") -> list[dict]:
    """Search DuckDuckGo and return a list of results.

    timelimit: 'd' day, 'w' week, 'm' month — hot takes use a tighter window
    so topics are actually current.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results, timelimit=timelimit))
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "description": r.get("body", ""),
        }
        for r in results
    ]


def run_queries(queries: list[str], label: str, timelimit: str) -> list[dict]:
    """Run a list of queries and collect findings."""
    findings = []
    print(f"Running {len(queries)} {label} queries via DuckDuckGo...")

    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] {label}: {query}")
        try:
            results = ddg_search(query, timelimit=timelimit)
            findings.append(
                {
                    "track": label,
                    "query": query,
                    "results": results,
                    "result_count": len(results),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            print(f"    Warning: search failed ({e}), skipping.")
            findings.append(
                {
                    "track": label,
                    "query": query,
                    "results": [],
                    "result_count": 0,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        if i < len(queries):
            time.sleep(2)  # polite delay to avoid rate limiting

    return findings


def format_results_section(finding: dict) -> str:
    """Format a single query's results as a markdown section."""
    lines = [f"### {finding['query']}\n"]

    if not finding["results"]:
        lines.append("_No results found or search failed._\n")
        return "\n".join(lines)

    for j, r in enumerate(finding["results"], 1):
        lines.append(f"**{j}. {r['title']}**")
        if r.get("description"):
            lines.append(f"> {r['description']}")
        lines.append(f"- {r['url']}")
        lines.append("")

    return "\n".join(lines)


def build_report(
    viral: list[dict], hot: list[dict], week_start: str, week_end: str
) -> str:
    """Build the full two-track weekly markdown report."""
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = sum(f["result_count"] for f in viral + hot)

    lines = [
        f"# Instagram Content Research — Week of {week_start}",
        "",
        f"_Generated: {generated_at} | Period: {week_start} → {week_end} | "
        f"Total results: {total}_",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"Two research tracks across **{len(viral) + len(hot)} queries**:",
        "",
        "1. **Viral content** — hooks & formats working right now in your niches.",
        "2. **Hot takes** — trending topics to react to with your opinionated "
        "\"angry breakdown\" commentary style.",
        "",
        "**Niches covered:**",
    ]
    for niche in NICHES:
        lines.append(f"- {niche}")

    # Track 1
    lines += ["", "---", "", "## 🔥 Track 1 — Viral Content (hooks & formats)", ""]
    for finding in viral:
        lines.append(format_results_section(finding))
        lines.append("---")
        lines.append("")

    # Track 2
    lines += [
        "",
        "## 🎙️ Track 2 — Hot Takes (topics to react to)",
        "",
        "Scan these for a story that makes you genuinely react. The strongest "
        "commentary videos pair a *current* topic with a *strong angle*.",
        "",
        "**Angles that reliably land:**",
    ]
    for angle in HOT_TAKE_ANGLES:
        lines.append(f"- {angle}")
    lines.append("")

    for finding in hot:
        lines.append(format_results_section(finding))
        lines.append("---")
        lines.append("")

    lines += [
        "## How to Use This Report",
        "",
        "**For viral content (Track 1):** study the hooks and formats — copy "
        "exact phrasing from high-performing headlines, note which formats recur, "
        "and model your next Reel on 2-3 examples.",
        "",
        "**For hot takes (Track 2):** pick ONE topic that makes you react, choose "
        "an angle from the list above, and open with your take in the first 2 "
        "seconds (\"Can we talk about...\", \"Unpopular opinion:...\"). Strong "
        "opinion + current topic = comments = reach.",
        "",
        "_Re-run each Monday for a fresh weekly snapshot._",
    ]

    return "\n".join(lines)


def save_outputs(
    viral: list[dict], hot: list[dict], report: str, week_start: str
) -> tuple[str, str]:
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
                "niches_researched": NICHES,
                "viral_queries": VIRAL_QUERIES,
                "hot_take_queries": HOT_TAKE_QUERIES,
                "viral_findings": viral,
                "hot_take_findings": hot,
            },
            indent=2,
        )
    )

    md_path = output_dir / f"weekly_report_{date_slug}.md"
    md_path.write_text(report)

    return str(json_path), str(md_path)


def main():
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_start_str = str(week_start)
    week_end_str = str(week_end)

    print(f"\n=== Instagram Content Research: Week of {week_start_str} ===\n")

    viral = run_queries(VIRAL_QUERIES, "viral", timelimit="m")
    hot = run_queries(HOT_TAKE_QUERIES, "hot-take", timelimit="w")

    report = build_report(viral, hot, week_start_str, week_end_str)
    json_path, md_path = save_outputs(viral, hot, report, week_start_str)

    print("\n=== Research Complete ===")
    print(f"Raw findings : {json_path}")
    print(f"Weekly report: {md_path}")


if __name__ == "__main__":
    main()
