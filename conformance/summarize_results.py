#!/usr/bin/env python3
"""Render oztest JSON results as a Markdown report.

Used by the conformance GitHub Actions workflow to write the job summary:
    python conformance/summarize_results.py results.json >> "$GITHUB_STEP_SUMMARY"
"""

import collections
import html
import json
import sys

STATUSES = ["pass", "fail", "xfail", "error", "skip"]
ICONS = {"pass": "✅", "fail": "❌", "xfail": "⚠️", "error": "💥", "skip": "⏭️"}
MAX_MESSAGE_LENGTH = 300


def format_message(message: str) -> str:
    """Make a free-text message safe to put in a Markdown table cell."""
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH] + "…"
    message = html.escape(message).replace("|", "&#124;")
    return "<br>".join(line for line in message.splitlines() if line.strip())


def main(path: str) -> None:
    """Print a Markdown report of the oztest results in the JSON file at `path`."""
    with open(path) as f:
        out = json.load(f)
    results = out["results"]

    by_version = collections.defaultdict(list)
    for result in results:
        by_version[result["oz_version"]].append(result)

    print(f"## `parse_attributes` conformance (oztest {out['oztest_version']})")
    print()
    print("| OME-Zarr version | " + " | ".join(STATUSES) + " | total |")
    print("| --- |" + " ---: |" * (len(STATUSES) + 1))
    for version, version_results in sorted(by_version.items()):
        counts = collections.Counter(r["result"] for r in version_results)
        cells = " | ".join(str(counts[s]) for s in STATUSES)
        print(f"| {version} | {cells} | {len(version_results)} |")

    for version, version_results in sorted(by_version.items()):
        # Show non-passing cases first
        version_results.sort(key=lambda r: (r["result"] == "pass", r["slug"]))
        n_pass = sum(r["result"] == "pass" for r in version_results)
        print()
        print(
            f"<details><summary><b>v{version}</b>: "
            f"{n_pass}/{len(version_results)} passing</summary>"
        )
        print()
        print("| | case | message |")
        print("| --- | --- | --- |")
        for result in version_results:
            icon = ICONS.get(result["result"], result["result"])
            # Drop the "{kind}/v{version}/{profile}/" prefix shared by the section
            case = f"{result['profile']}/{result['expected_validity']}/{result['name']}"
            message = format_message(result.get("message") or "")
            print(f"| {icon} | `{case}` | {message} |")
        print()
        print("</details>")

    print()
    print(
        "Legend: "
        + ", ".join(f"{ICONS[s]} {s}" for s in STATUSES)
        + ". Full results are attached to this run as an artifact."
    )


if __name__ == "__main__":
    main(sys.argv[1])
