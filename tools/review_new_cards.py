#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "cards"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
CARD_PATH_RE = re.compile(r"^cards/[^/]+/[^/]+\.md$")
REQUIRED_FIELDS = [
    "id",
    "title",
    "technologies",
    "areas",
    "tags",
    "difficulty",
    "question",
]
KNOWN_DIFFICULTIES = {"junior", "mid", "senior"}


@dataclass
class Finding:
    severity: str
    path: str
    message: str


@dataclass
class Card:
    path: str
    meta: dict[str, object]
    body: str

    @property
    def card_id(self) -> str:
        return str(self.meta.get("id", ""))

    @property
    def question(self) -> str:
        return str(self.meta.get("question", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Review generated flashcards on auto branches.")
    parser.add_argument("--base", default="origin/main", help="Base ref to compare against.")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    findings: list[Finding] = []
    base_ref = ensure_base_ref(args.base, findings)
    changed_paths = changed_card_paths(base_ref)

    if not changed_paths:
        print("No changed card files to review.")
        return 0

    current_cards = load_current_cards(findings)
    base_cards = load_base_cards(base_ref, findings)

    current_ids = index_by_id(current_cards, findings)
    base_ids = {card.card_id for card in base_cards if card.card_id}
    base_questions = {normalize_question(card.question): card for card in base_cards if card.question}

    for path in changed_paths:
        card = current_cards.get(path)
        if not card:
            findings.append(Finding("fail", path, "Changed card file is missing from the working tree."))
            continue

        review_card_shape(card, findings)
        review_duplicate_question(card, base_questions, findings)
        review_new_card_metadata(card, base_ids, findings)

    print_report(findings, changed_paths, current_ids)
    has_failures = any(finding.severity == "fail" for finding in findings)
    has_warnings = any(finding.severity == "warn" for finding in findings)

    if has_failures or (args.strict_warnings and has_warnings):
        return 1

    return 0


def ensure_base_ref(base_ref: str, findings: list[Finding]) -> str:
    if git(["rev-parse", "--verify", f"{base_ref}^{{commit}}"], check=False).returncode == 0:
        return base_ref

    fetch = git(["fetch", "origin", "main:refs/remotes/origin/main"], check=False)
    if fetch.returncode == 0 and git(["rev-parse", "--verify", "origin/main^{commit}"], check=False).returncode == 0:
        return "origin/main"

    findings.append(Finding("warn", "-", f"Base ref {base_ref!r} not found; reviewing changed files against HEAD only."))
    return "HEAD"


def changed_card_paths(base_ref: str) -> list[str]:
    if base_ref == "HEAD":
        return [str(path.relative_to(ROOT)) for path in CARDS_DIR.glob("*/*.md")]

    merge_base = git_stdout(["merge-base", base_ref, "HEAD"]).strip()
    diff = git_stdout(["diff", "--name-status", "--diff-filter=AMR", merge_base, "HEAD", "--", "cards"])
    paths: list[str] = []

    for line in diff.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        path = parts[-1]
        if CARD_PATH_RE.match(path):
            paths.append(path)

    return sorted(set(paths))


def load_current_cards(findings: list[Finding]) -> dict[str, Card]:
    cards: dict[str, Card] = {}
    for path in sorted(CARDS_DIR.glob("*/*.md")):
        rel_path = str(path.relative_to(ROOT))
        try:
            cards[rel_path] = parse_card(rel_path, path.read_text(encoding="utf-8"))
        except ValueError as error:
            findings.append(Finding("fail", rel_path, str(error)))
    return cards


def load_base_cards(base_ref: str, findings: list[Finding]) -> list[Card]:
    if base_ref == "HEAD":
        return []

    result = git(["ls-tree", "-r", "--name-only", base_ref, "cards"], check=False, text=True)
    if result.returncode != 0:
        findings.append(Finding("warn", "-", f"Could not list cards in {base_ref}."))
        return []

    cards: list[Card] = []
    for rel_path in result.stdout.splitlines():
        if not CARD_PATH_RE.match(rel_path):
            continue
        show = git(["show", f"{base_ref}:{rel_path}"], check=False, text=True)
        if show.returncode != 0:
            findings.append(Finding("warn", rel_path, f"Could not read base version from {base_ref}."))
            continue
        try:
            cards.append(parse_card(rel_path, show.stdout))
        except ValueError as error:
            findings.append(Finding("warn", rel_path, f"Base card parse issue: {error}"))
    return cards


def parse_card(path: str, source: str) -> Card:
    match = re.match(r"^---\n([\s\S]*?)\n---\n?([\s\S]*)$", source)
    if not match:
        raise ValueError("Missing YAML frontmatter block.")

    meta: dict[str, object] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {raw_line!r}")
        key, raw_value = line.split(":", 1)
        meta[key.strip()] = parse_yaml_value(raw_value.strip())

    return Card(path=path, meta=meta, body=match.group(2).strip())


def parse_yaml_value(raw_value: str) -> object:
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [unquote(item.strip()) for item in inner.split(",") if item.strip()]
    return unquote(raw_value)


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def index_by_id(cards: dict[str, Card], findings: list[Finding]) -> dict[str, Card]:
    indexed: dict[str, Card] = {}
    for card in cards.values():
        if not card.card_id:
            continue
        previous = indexed.get(card.card_id)
        if previous:
            findings.append(Finding("fail", card.path, f"Duplicate card id also used by {previous.path}: {card.card_id}"))
        indexed[card.card_id] = card
    return indexed


def review_card_shape(card: Card, findings: list[Finding]) -> None:
    for field in REQUIRED_FIELDS:
        value = card.meta.get(field)
        if value in (None, "", []):
            findings.append(Finding("fail", card.path, f"Missing required frontmatter field: {field}"))

    if not ID_RE.match(card.card_id):
        findings.append(Finding("fail", card.path, f"Invalid id slug: {card.card_id!r}"))

    expected_slug = card.card_id.split(".", 1)[-1]
    actual_slug = Path(card.path).stem
    if expected_slug and actual_slug != expected_slug:
        findings.append(Finding("warn", card.path, f"File slug {actual_slug!r} does not match id slug {expected_slug!r}."))

    for field in ["technologies", "areas", "tags"]:
        values = card.meta.get(field)
        if not isinstance(values, list):
            findings.append(Finding("fail", card.path, f"{field} must be an inline array."))
            continue
        if not values:
            findings.append(Finding("fail", card.path, f"{field} must not be empty."))
        for value in values:
            if not isinstance(value, str) or not SLUG_RE.match(value):
                findings.append(Finding("fail", card.path, f"{field} contains invalid slug: {value!r}"))

    difficulty = card.meta.get("difficulty")
    if isinstance(difficulty, str) and difficulty not in KNOWN_DIFFICULTIES:
        findings.append(Finding("warn", card.path, f"Unexpected difficulty {difficulty!r}; known values: {sorted(KNOWN_DIFFICULTIES)}."))

    title = str(card.meta.get("title", ""))
    if len(title) < 8:
        findings.append(Finding("warn", card.path, "Title looks too short."))

    question = card.question
    if len(question) < 30:
        findings.append(Finding("warn", card.path, "Question looks too short for an interview flashcard."))
    if not question.endswith("?"):
        findings.append(Finding("warn", card.path, "Question should usually end with a question mark."))

    if len(card.body) < 180:
        findings.append(Finding("warn", card.path, "Answer body is very short; review whether it is useful as a study card."))

    forbidden_fragments = [
        "### pytanie",
        "### moja odpowied",
        "## moja odpowied",
        "odpowiedz ai",
        "lepsza odpowied",
        "as an ai",
        "jako model",
    ]
    combined = f"{title}\n{question}\n{card.body}".lower()
    for fragment in forbidden_fragments:
        if fragment in combined:
            findings.append(Finding("fail", card.path, f"Card appears to contain raw source/log marker: {fragment!r}"))


def review_duplicate_question(card: Card, base_questions: dict[str, Card], findings: list[Finding]) -> None:
    normalized = normalize_question(card.question)
    if not normalized:
        return

    existing = base_questions.get(normalized)
    if existing and existing.card_id != card.card_id:
        if not (ROOT / existing.path).exists():
            return
        findings.append(
            Finding(
                "fail",
                card.path,
                f"Question duplicates existing card {existing.card_id} from {existing.path}.",
            )
        )


def review_new_card_metadata(card: Card, base_ids: set[str], findings: list[Finding]) -> None:
    if card.card_id in base_ids:
        return

    source_repo = card.meta.get("source_repo")
    source_path = card.meta.get("source_path")
    source_hash = card.meta.get("source_hash")

    if source_repo is not None and (not isinstance(source_repo, str) or not source_repo.strip()):
        findings.append(Finding("warn", card.path, "source_repo should be a non-empty string when provided."))
    if source_path is not None and (not isinstance(source_path, str) or not source_path.strip()):
        findings.append(Finding("warn", card.path, "source_path should be a non-empty string when provided."))
    if source_hash is not None and (not isinstance(source_hash, str) or len(source_hash) < 16):
        findings.append(Finding("warn", card.path, "source_hash should be a stable hash-like string when provided."))


def normalize_question(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ąćęłńóśźż]+", " ", value.lower())).strip()


def print_report(findings: list[Finding], changed_paths: list[str], current_ids: dict[str, Card]) -> None:
    print("# Flashcard branch review")
    print()
    print(f"Changed card files: {len(changed_paths)}")
    print(f"Current card ids: {len(current_ids)}")
    print()

    if not findings:
        print("No findings.")
        return

    for severity in ["fail", "warn"]:
        scoped = [finding for finding in findings if finding.severity == severity]
        if not scoped:
            continue
        print(f"## {severity.upper()}")
        for finding in scoped:
            print(f"- `{finding.path}`: {finding.message}")
        print()


def git_stdout(args: list[str]) -> str:
    return git(args, text=True).stdout


def git(args: list[str], check: bool = True, text: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )


if __name__ == "__main__":
    sys.exit(main())
