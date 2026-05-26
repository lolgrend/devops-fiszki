from __future__ import annotations

import re


REDACTION = "[redacted]"

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*['\"]?[^'\"\s`]{12,}"),
]


def redact_sensitive_text(value: object) -> str:
    text = str(value or "")
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(REDACTION, text)
    return text
