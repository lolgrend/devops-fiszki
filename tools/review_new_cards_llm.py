#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import urllib.error
import urllib.request

from review_new_cards import Finding, changed_card_paths, ensure_base_ref, git_stdout, load_current_cards


DEFAULT_MODEL = "gpt-5.4-mini"


def main() -> int:
    parser = argparse.ArgumentParser(description="Review changed flashcards with an OpenAI-compatible LLM.")
    parser.add_argument("--base", default="origin/main", help="Base ref to compare against.")
    parser.add_argument("--model", default=os.environ.get("LITE_LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--optional", action="store_true", help="Skip cleanly when LiteLLM env vars are missing.")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat LLM warnings as failures.")
    args = parser.parse_args()

    base_url = os.environ.get("LITE_LLM_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("LITE_LLM_KEY", "")

    if not base_url or not api_key:
        message = "LLM card review skipped: LITE_LLM_BASE_URL and/or LITE_LLM_KEY are not configured."
        if args.optional:
            print(message)
            return 0
        print(message, file=sys.stderr)
        return 1

    findings: list[Finding] = []
    base_ref = ensure_base_ref(args.base, findings)
    changed_paths = changed_card_paths(base_ref)

    if findings:
        for finding in findings:
            print(f"{finding.severity}: {finding.path}: {finding.message}", file=sys.stderr)

    if not changed_paths:
        print("LLM card review: no changed card files to review.")
        return 0

    current_cards = load_current_cards(findings)
    if any(finding.severity == "fail" for finding in findings):
        for finding in findings:
            print(f"{finding.severity}: {finding.path}: {finding.message}", file=sys.stderr)
        return 1

    has_fail = False
    has_warn = False
    branch_name = current_branch_name()
    print("# LLM flashcard review")
    print()

    for index, path in enumerate(changed_paths, start=1):
        card = current_cards.get(path)
        if not card:
            print(f"## {index}. `{path}` — {format_verdict_label('fail')}")
            print()
            print("Changed card file is missing.")
            print()
            has_fail = True
            continue

        review = review_card(base_url, api_key, args.model, card)
        verdict = normalize_verdict(review.get("verdict"))
        topic = normalize_inline(review.get("topic") or card.meta.get("title") or card.card_id)
        reason = normalize_inline(review.get("reason") or "No reason returned.")
        basis = normalize_inline(review.get("documentation_basis") or "")

        print(f"## {index}. `{card.card_id}` — {format_verdict_label(verdict)}")
        print()
        if topic:
            print(f"**Topic:** {topic}")
            print()
        print(f"**Reason:** {reason}")
        print()
        if basis:
            print(f"**Basis:** {basis}")
            print()

        if verdict in {"warn", "fail"}:
            print_remediation(card, review, branch_name)

        if verdict == "warn":
            has_warn = True
        if verdict == "fail":
            has_fail = True

    if args.strict_warnings and has_warn:
        print()
        print("LLM card review failed because --strict-warnings is enabled and at least one card returned warn.")

    return 1 if has_fail or (args.strict_warnings and has_warn) else 0


VERDICT_LABELS = {
    "pass": "**PASS**",
    "warn": "**WARN**",
    "fail": "**FAIL**",
}


def format_verdict_label(verdict: str) -> str:
    return VERDICT_LABELS.get(verdict, "**WARN**")


def review_card(base_url: str, api_key: str, model: str, card) -> dict[str, object]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior DevOps reviewer checking generated flashcards for technical accuracy. "
                    "Review only the supplied card. Be strict about dangerous advice, hallucinated commands, "
                    "incorrect Kubernetes/Terraform/AWS behavior, and vague non-actionable answers. "
                    "Return JSON only with keys: verdict, topic, reason, documentation_basis, "
                    "suggested_action, suggested_answer_markdown. "
                    "verdict must be one of: pass, warn, fail. "
                    "Use pass for technically sound cards, warn for useful but incomplete cards, "
                    "and fail for materially wrong or unsafe cards. "
                    "documentation_basis should be short, e.g. 'Kubernetes HPA behavior', "
                    "'Terraform state locking behavior', or an empty string if unsure. "
                    "For warn or fail, suggested_action should say what to change in the card. "
                    "For warn or fail, suggested_answer_markdown should contain a complete replacement "
                    "for the answerMarkdown field. For pass, return empty strings for both suggestions."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "id": card.card_id,
                        "title": card.meta.get("title"),
                        "technologies": card.meta.get("technologies"),
                        "areas": card.meta.get("areas"),
                        "tags": card.meta.get("tags"),
                        "difficulty": card.meta.get("difficulty"),
                        "question": card.question,
                        "answerMarkdown": truncate(card.body, 7000),
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        return call_chat_completions(base_url, api_key, payload)
    except RuntimeError as error:
        if "response_format" not in str(error).lower():
            raise

    payload.pop("response_format", None)
    return call_chat_completions(base_url, api_key, payload)


def call_chat_completions(base_url: str, api_key: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LiteLLM HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach LiteLLM endpoint: {error.reason}") from error

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"Unexpected LiteLLM response shape: {data!r}") from error

    return parse_json_object(content)


def parse_json_object(content: str) -> dict[str, object]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError(f"LLM did not return JSON: {content!r}")
        value = json.loads(content[start : end + 1])

    if not isinstance(value, dict):
        raise RuntimeError(f"LLM JSON response is not an object: {value!r}")
    return value


def normalize_verdict(value: object) -> str:
    verdict = str(value or "warn").strip().lower()
    if verdict in {"pass", "ok", "good", "looks-good"}:
        return "pass"
    if verdict in {"fail", "failed", "bad", "unsafe", "wrong"}:
        return "fail"
    return "warn"


def normalize_inline(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_block(value: object) -> str:
    return str(value or "").strip()


def print_remediation(card, review: dict[str, object], branch_name: str) -> None:
    path = card.path
    suggested_action = normalize_block(review.get("suggested_action"))
    suggested_answer = normalize_block(review.get("suggested_answer_markdown"))
    source_hash = normalize_inline(card.meta.get("source_hash"))
    source_path = normalize_inline(card.meta.get("source_path"))

    print(f"### Remediation for `{path}`")
    print()
    print("Edit the card, review the suggested answer, then rerun validation.")
    print()
    if suggested_action:
        print("**Suggested change:**")
        print()
        print(suggested_action)
        print()

    print("**Commands:**")
    print()
    print("```bash")
    print("git fetch origin")
    print(f"git checkout {shlex.quote(branch_name)}")
    print(f"git pull --ff-only origin {shlex.quote(branch_name)}")
    print(f"${{EDITOR:-vi}} {shlex.quote(path)}")
    print("npm run check")
    print("npm run review:auto")
    print("npm run review:auto:llm")
    print("```")
    print()

    print("**Or reject this card from the import branch:**")
    print()
    print("```bash")
    print(f"git rm {shlex.quote(path)}")
    print("npm run check")
    print("npm run review:auto")
    print("npm run review:auto:llm")
    print("```")
    print()

    if source_hash:
        print("**Persistent reject key for the generator:**")
        print()
        print("```text")
        if source_path:
            print(f"source_path={source_path}")
        print(f"source_hash={source_hash}")
        print("```")
        print()

    if suggested_answer:
        print("**Suggested answerMarkdown:**")
        print()
        print_fenced("md", suggested_answer)
        print()


def current_branch_name() -> str:
    for env_name in ["GITHUB_HEAD_REF", "GITEA_HEAD_REF", "GITHUB_REF_NAME", "GITEA_REF_NAME", "CI_COMMIT_REF_NAME"]:
        value = os.environ.get(env_name, "").strip()
        if value:
            return value

    ref = os.environ.get("GITHUB_REF", "").strip()
    if ref.startswith("refs/heads/"):
        return ref.removeprefix("refs/heads/")

    try:
        value = git_stdout(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    except Exception:
        value = ""

    if value and value != "HEAD":
        return value
    return "<generated-card-branch>"


def print_fenced(language: str, content: str) -> None:
    longest = 2
    current = 0
    for char in content:
        if char == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    fence = "`" * (longest + 1)
    print(f"{fence}{language}")
    print(content)
    print(fence)


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return f"{value[:limit]}\n\n[truncated]"


if __name__ == "__main__":
    sys.exit(main())
