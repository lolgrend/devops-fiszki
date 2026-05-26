#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from output_safety import redact_sensitive_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a sanitized pull request review comment.")
    parser.add_argument("--deterministic-file", default="deterministic-review.md")
    parser.add_argument("--llm-file", default="llm-review.md")
    parser.add_argument("--output", default="card-review-comment.md")
    args = parser.parse_args()

    deterministic = read_text(args.deterministic_file, "Deterministic review did not produce output.")
    llm_review = read_text(args.llm_file, "LLM review did not produce output.")

    body = "\n".join(
        [
            "## Card review",
            "",
            "### Deterministic review",
            "",
            "```text",
            deterministic.rstrip(),
            "```",
            "",
            "### Optional LLM review",
            "",
            demote_headings(llm_review.rstrip()),
            "",
        ]
    )

    Path(args.output).write_text(redact_sensitive_text(body), encoding="utf-8")
    return 0


def read_text(path: str, fallback: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return fallback
    text = file_path.read_text(encoding="utf-8").strip()
    return redact_sensitive_text(text or fallback)


def demote_headings(markdown: str) -> str:
    lines = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            lines.append(f"#{line}")
        else:
            lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
