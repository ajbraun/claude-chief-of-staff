#!/usr/bin/env python3
"""
LinkedIn Phase 2 — Targeted Web Search
Reads Notes/active/linkedin-phase2-list.json, searches each pending contact,
writes findings back. Safe to stop and restart — state is checkpointed after
every contact.

Usage:
  python3 scripts/phase2-search.py            # process up to MAX_PER_RUN contacts
  python3 scripts/phase2-search.py --status   # show progress summary only
"""

import json
import subprocess
import sys
import time
import datetime
import re
import argparse
from pathlib import Path

LIST_FILE = Path("Notes/active/linkedin-phase2-list.json")
SLEEP_BETWEEN = 20   # seconds between searches (respect rate limits)
MAX_PER_RUN = 25     # max contacts per invocation

PROMPT_TEMPLATE = """Search for {name}, who was previously at {company} as "{position}".

Goal: {goal}

Do a web search for their name and company. Find what they are doing NOW.

Return ONLY a valid JSON object — no explanation, no markdown, just raw JSON:
{{"current_role": "their current title", "current_company": "their current employer", "summary": "2-3 sentences on what they are working on now and anything notable", "source_url": "url where you found this", "notable": false}}

Set "notable" to true if this person looks interesting for any of:
- Layr pipeline (AI/data/annotation companies, decision-maker level)
- Job search (senior role at a company Andy would want to work at)
- Consulting (senior decision-maker at mid-market tech company)
- Reactivation (impressive move since last contact)

If you cannot find current info, return:
{{"current_role": "unknown", "current_company": "unknown", "summary": "No current information found.", "source_url": "", "notable": false}}"""


def load_list():
    with open(LIST_FILE) as f:
        return json.load(f)


def save_list(data):
    with open(LIST_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def search_contact(contact):
    prompt = PROMPT_TEMPLATE.format(
        name=contact["name"],
        company=contact["company"],
        position=contact["position"],
        goal=contact["goal"],
    )

    try:
        env = {k: v for k, v in __import__("os").environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            ["claude", "--print", "-y", prompt],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=Path(__file__).parent.parent,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"

    output = result.stdout.strip()
    stderr = result.stderr.strip()

    # Detect rate limit in either stdout or stderr
    combined = (output + stderr).lower()
    if any(phrase in combined for phrase in ["rate limit", "too many requests", "429", "overloaded"]):
        return None, "rate_limit"

    if result.returncode != 0 and not output:
        return None, f"error_exit_{result.returncode}"

    # Extract JSON — Claude sometimes wraps it in markdown or adds text
    # Try strict parse first, then extract from surrounding text
    try:
        return json.loads(output), "ok"
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'\{[^{}]*"current_role"[^{}]*\}', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group()), "ok"
        except json.JSONDecodeError:
            pass

    return {"summary": output[:500], "current_role": "unknown", "current_company": "unknown", "source_url": "", "notable": False}, "parse_warn"


def print_status(data):
    contacts = data["contacts"]
    from collections import Counter
    statuses = Counter(c.get("status", "pending") for c in contacts)
    notable = [c for c in contacts if c.get("notable") and c.get("status") == "done"]

    print(f"\nPhase 2 Progress — {data.get('created', 'unknown')}")
    print(f"  Total:   {len(contacts)}")
    print(f"  Pending: {statuses.get('pending', 0)}")
    print(f"  Done:    {statuses.get('done', 0)}")
    print(f"  Error:   {statuses.get('error', 0)}")
    print(f"  Notable: {len(notable)}")

    if notable:
        print(f"\nNotable finds so far:")
        for c in notable:
            print(f"  [{c['bucket']}] {c['name']} — {c.get('current_role','?')} @ {c.get('current_company','?')}")
            print(f"         {c.get('summary','')[:100]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="Show progress only, no searching")
    parser.add_argument("--max", type=int, default=MAX_PER_RUN, help="Max contacts to process this run")
    args = parser.parse_args()

    if not LIST_FILE.exists():
        print(f"ERROR: {LIST_FILE} not found. Run phase 1 first.")
        sys.exit(1)

    data = load_list()

    if args.status:
        print_status(data)
        return

    contacts = data["contacts"]
    pending = [c for c in contacts if c.get("status") == "pending"]
    print(f"Starting run — {len(pending)} pending contacts, processing up to {args.max}")
    print(f"Checkpoint file: {LIST_FILE}\n")

    processed = 0
    for c in contacts:
        if c.get("status") != "pending":
            continue
        if processed >= args.max:
            print(f"\nReached max per run ({args.max}). Stopping cleanly.")
            break

        print(f"[{processed + 1}/{min(len(pending), args.max)}] {c['name']:30s} ({c['bucket']}) ... ", end="", flush=True)

        findings, status = search_contact(c)

        if status == "rate_limit":
            print("RATE LIMIT — saving state and stopping.")
            save_list(data)
            print_status(data)
            sys.exit(0)

        if findings:
            c.update(findings)
            c["status"] = "done" if status == "ok" else "error"
            c["searched_at"] = datetime.datetime.now().isoformat()
            flag = " ★" if c.get("notable") else ""
            print(f"{c.get('current_company', '?')[:30]}{flag}")
        else:
            c["status"] = "error"
            c["error"] = status
            print(f"✗ {status}")

        save_list(data)
        processed += 1

        if processed < args.max and c.get("status") != "error":
            time.sleep(SLEEP_BETWEEN)

    print()
    print_status(data)


if __name__ == "__main__":
    main()
