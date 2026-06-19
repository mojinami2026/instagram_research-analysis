"""Weekly Instagram viral video research for personal brand niches."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import anthropic

from config import (
    ANALYSIS_DIMENSIONS,
    PERSONAL_BRAND_NICHES,
    REPORT_OUTPUT_DIR,
    RESEARCH_QUERIES,
)

RESEARCH_SYSTEM_PROMPT = """You are an expert social media analyst specializing in Instagram content strategy and personal branding.

Your task is to research and analyze viral Instagram videos in the personal brand niche. For each research query:
1. Search for recent viral Instagram Reels and posts (past 7 days preferred, past 30 days acceptable)
2. Identify patterns in hooks, formats, engagement tactics, and content themes
3. Extract actionable insights for personal brand content creators

Focus on:
- Video hooks (first 3 seconds)
- Content formats (talking head, b-roll, text overlay, carousel-style reels)
- Engagement drivers (controversy, value, inspiration, entertainment)
- Trending audio, sounds, or text styles
- Caption and CTA patterns
- Estimated reach/virality indicators

Be specific, data-driven where possible, and focus on patterns that can be replicated."""

SYNTHESIS_PROMPT = """Based on all the research above, create a comprehensive weekly report with:

1. **TOP VIRAL PATTERNS THIS WEEK** — 5 most recurring patterns observed across all searches
2. **WINNING HOOKS** — 10 specific hook formulas that appeared in viral content (with examples)
3. **CONTENT FORMATS TRENDING** — Which video formats are performing best (ranked)
4. **NICHE BREAKDOWN** — Key observations per personal brand sub-niche
5. **ENGAGEMENT TACTICS** — 5 specific tactics driving comments and shares
6. **ACTIONABLE RECOMMENDATIONS** — 7 concrete content ideas to create this week based on findings
7. **WHAT TO AVOID** — 3 content patterns that are underperforming or oversaturated

Format the output as a structured markdown report with clear headers and bullet points.
Include a "WEEKLY SUMMARY" executive summary at the top (3-4 sentences).
"""


def run_research(client: anthropic.Anthropic) -> list[dict]:
    """Run web searches for each research query and collect findings."""
    findings = []

    print(f"Running {len(RESEARCH_QUERIES)} research queries...")

    for i, query in enumerate(RESEARCH_QUERIES, 1):
        print(f"  [{i}/{len(RESEARCH_QUERIES)}] Searching: {query}")

        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            system=RESEARCH_SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[
                {
                    "role": "user",
                    "content": f"Research this query and provide detailed findings about viral Instagram content in the personal brand niche: '{query}'\n\nFor each viral video or content pattern you find, note: the hook, format, niche, engagement drivers, and what makes it shareable. Search for content from the past 7-30 days.",
                }
            ],
        )

        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        findings.append(
            {
                "query": query,
                "findings": result_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    return findings


def synthesize_report(
    client: anthropic.Anthropic, findings: list[dict], week_start: str, week_end: str
) -> str:
    """Synthesize all research findings into a weekly report."""
    print("Synthesizing findings into weekly report...")

    combined_findings = "\n\n---\n\n".join(
        [f"## Research Query: {f['query']}\n\n{f['findings']}" for f in findings]
    )

    messages = [
        {
            "role": "user",
            "content": f"Here are the research findings from {len(findings)} searches about viral Instagram content in personal brand niches for the week of {week_start} to {week_end}:\n\n{combined_findings}",
        },
        {
            "role": "assistant",
            "content": "I've reviewed all the research findings. Now I'll synthesize these into a comprehensive weekly report.",
        },
        {"role": "user", "content": SYNTHESIS_PROMPT},
    ]

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        system=RESEARCH_SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text


def save_report(findings: list[dict], report: str, week_start: str) -> tuple[str, str]:
    """Save the raw findings (JSON) and final report (Markdown)."""
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
    header = f"# Instagram Viral Video Research — Week of {week_start}\n\n_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_\n\n---\n\n"
    md_path.write_text(header + report)

    return str(json_path), str(md_path)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_start_str = str(week_start)
    week_end_str = str(week_end)

    print(f"\n=== Instagram Viral Research: Week of {week_start_str} ===\n")

    findings = run_research(client)
    report = synthesize_report(client, findings, week_start_str, week_end_str)
    json_path, md_path = save_report(findings, report, week_start_str)

    print(f"\n=== Research Complete ===")
    print(f"Raw findings saved to: {json_path}")
    print(f"Weekly report saved to: {md_path}")
    print("\n--- REPORT PREVIEW (first 500 chars) ---")
    print(report[:500] + "...")


if __name__ == "__main__":
    main()
