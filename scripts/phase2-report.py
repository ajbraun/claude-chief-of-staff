#!/usr/bin/env python3
"""
LinkedIn Phase 2 — Report Generator
Reads completed search results and writes a markdown report to Notes/active/.

Usage:
  python3 scripts/phase2-report.py
"""

import json
import datetime
from pathlib import Path
from collections import defaultdict

LIST_FILE = Path("Notes/active/linkedin-phase2-list.json")
REPORT_FILE = Path("Notes/active/linkedin-phase2-report.md")


def main():
    with open(LIST_FILE) as f:
        data = json.load(f)

    contacts = data["contacts"]
    done = [c for c in contacts if c.get("status") == "done"]
    notable = [c for c in done if c.get("notable")]
    errors = [c for c in contacts if c.get("status") == "error"]
    pending = [c for c in contacts if c.get("status") == "pending"]

    by_bucket = defaultdict(list)
    notable_by_bucket = defaultdict(list)
    for c in done:
        by_bucket[c["bucket"]].append(c)
        if c.get("notable"):
            notable_by_bucket[c["bucket"]].append(c)

    bucket_labels = {
        "B1": "Dormant Senior (2010–2013)",
        "B2": "Toloka/Nebius Senior",
        "B3": "Microsoft Senior",
        "B4": "Annotation/Data Competitive Intel",
    }

    lines = []
    lines.append(f"# LinkedIn Phase 2 Report")
    lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Searched:** {len(done)}/{len(contacts)} contacts | **Notable:** {len(notable)} | **Errors:** {len(errors)} | **Pending:** {len(pending)}")
    lines.append("")

    if notable:
        lines.append("---")
        lines.append("")
        lines.append("## ★ Notable Finds")
        lines.append("")
        for b in ["B1", "B2", "B3", "B4"]:
            group = notable_by_bucket.get(b, [])
            if not group:
                continue
            lines.append(f"### {b} — {bucket_labels[b]}")
            lines.append("")
            for c in group:
                lines.append(f"**{c['name']}**")
                lines.append(f"- Was: {c['position']} @ {c['company']}")
                lines.append(f"- Now: {c.get('current_role', '?')} @ {c.get('current_company', '?')}")
                lines.append(f"- {c.get('summary', '')}")
                if c.get("source_url"):
                    lines.append(f"- Source: {c['source_url']}")
                lines.append(f"- LinkedIn: {c['url']}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## All Results by Bucket")
    lines.append("")

    for b in ["B1", "B2", "B3", "B4"]:
        group = by_bucket.get(b, [])
        if not group:
            continue
        lines.append(f"### {b} — {bucket_labels[b]} ({len(group)} searched)")
        lines.append("")
        lines.append("| Name | Was | Now | Notable |")
        lines.append("|------|-----|-----|---------|")
        for c in group:
            name = f"[{c['name']}]({c['url']})" if c.get("url") else c["name"]
            was = f"{c['position'][:35]} @ {c['company'][:20]}"
            now = f"{c.get('current_role', '?')[:35]} @ {c.get('current_company', '?')[:20]}"
            flag = "★" if c.get("notable") else ""
            lines.append(f"| {name} | {was} | {now} | {flag} |")
        lines.append("")

    if errors:
        lines.append("---")
        lines.append("")
        lines.append(f"## Errors ({len(errors)})")
        lines.append("")
        for c in errors:
            lines.append(f"- {c['name']} ({c['bucket']}) — {c.get('error', 'unknown error')}")
        lines.append("")

    report = "\n".join(lines)
    with open(REPORT_FILE, "w") as f:
        f.write(report)

    print(f"Report written to {REPORT_FILE}")
    print(f"Notable: {len(notable)} | Done: {len(done)} | Pending: {len(pending)}")


if __name__ == "__main__":
    main()
