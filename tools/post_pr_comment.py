#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


MAX_BODY_LENGTH = 60000


def request(method: str, url: str, headers: dict, payload: dict | None = None):
    data = None
    request_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed with {error.code}: {detail}") from error
    return json.loads(content) if content else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post or update a marker-tagged comment on a GitHub pull request.",
    )
    parser.add_argument("--body-file", required=True, help="Path to a file containing the comment body.")
    parser.add_argument("--marker", required=True, help="HTML marker used to identify the bot comment to update.")
    args = parser.parse_args()

    if not os.path.exists(args.body_file):
        print(f"No comment body file at {args.body_file}; skipping PR comment.")
        return 0

    with open(args.body_file, encoding="utf-8") as handle:
        review_body = handle.read().strip()

    if not review_body:
        print("Comment body is empty; skipping PR comment.")
        return 0

    marker = args.marker
    if len(f"{marker}\n{review_body}\n") > MAX_BODY_LENGTH:
        review_body = (
            review_body[: MAX_BODY_LENGTH - len(marker) - 80].rstrip()
            + "\n\n_Output truncated; see the workflow log for the complete review._"
        )
    body = f"{marker}\n{review_body}\n"

    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    pr_number = os.environ["PR_NUMBER"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    comments_url = f"{api_url}/repos/{repo}/issues/{pr_number}/comments?per_page=100"
    comments = request("GET", comments_url, headers) or []
    existing = next(
        (
            comment
            for comment in comments
            if marker in comment.get("body", "")
            and comment.get("user", {}).get("type") == "Bot"
        ),
        None,
    )

    if existing:
        request("PATCH", existing["url"], headers, {"body": body})
        print(f"Updated PR comment: {existing['html_url']}")
    else:
        created = request("POST", comments_url, headers, {"body": body})
        print(f"Created PR comment: {created['html_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
