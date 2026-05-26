# DevOps Flashcards

**Live demo:** <https://lolgrend.github.io/devops-fiszki/>

This repository is a cleaned public showcase extracted from my private AI-assisted DevOps learning workflow. The private workflow generates candidate flashcards from structured notes; this public repo contains the deployable app, validation tooling and representative content.

## What It Is

DevOps Flashcards is a static browser app for practicing infrastructure and platform engineering topics before technical interviews. The current deck covers Terraform, Kubernetes, AWS, ECS/Fargate, CI/CD, rollout safety, drift handling, state management, RBAC, HPA, readiness, and production troubleshooting.

The project is intentionally small and deployable as static assets:

- one HTML application,
- Markdown flashcards with metadata,
- a generated JSON manifest,
- validation and review scripts,
- GitHub Actions workflows for CI.

## Why It Exists

The goal is to turn raw learning notes and interview-style questions into compact, repeatable cards. Each card is structured around practical operational judgement: what to check, how to reduce risk, what commands or platform mechanisms matter, and what trade-offs should be mentioned in a senior-level answer.

## Repository Layout

```text
cards/
  aws/
  bridges/
  kubernetes/
  terraform/
data/
  flashcards.json
tools/
  build-static.mjs
  generate-manifest.mjs
  review_new_cards.py
  review_new_cards_llm.py
index.html
package.json
```

## Local Workflow

Generate and validate the card manifest:

```bash
npm run check
```

Build static deployable assets:

```bash
npm run build
```

Run locally:

```bash
npm run check
npm run serve
```

Then open `http://localhost:4173`.

## Card Format

Each card is a Markdown file with YAML-like frontmatter:

```md
---
id: terraform.state-locking
title: State locking with remote backends
technologies: [terraform]
areas: [state]
tags: [state-locking, s3, collaboration]
difficulty: senior
question: What happens when two engineers run terraform apply against the same remote state?
---

State locking prevents concurrent writes to the same state.

- S3 can use native lock files.
- Older S3 setups often use DynamoDB.
- AzureRM uses blob leases.
```

The manifest generator validates required metadata, duplicate IDs, slug formats, and empty answers.

## CI/CD

GitHub Actions runs on GitHub-hosted runners and checks that the public showcase is reproducible without private infrastructure:

- validate card metadata and regenerate `data/flashcards.json`,
- build the static app into `dist/`,
- optionally run deterministic and LLM-assisted card review workflows when configured,
- deploy the static app to GitHub Pages after changes are merged to `main`.

The LLM review script can use the OpenAI API directly:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`, optional; defaults to `gpt-5.4-mini`
- `MAX_LLM_REVIEW_CARDS`, optional; defaults to `5`
- `MAX_LLM_CARD_CHARS`, optional; defaults to `4500`
- `MAX_LLM_COMPLETION_TOKENS`, optional; defaults to `2000`

It also supports an OpenAI-compatible gateway such as LiteLLM:

- `LITE_LLM_BASE_URL`
- `LITE_LLM_MODEL`
- `LITE_LLM_KEY`

Without either credential path, the optional review exits cleanly.

## AI-Assisted Workflow

Cards are LLM-generated in a private repo; this public repo is the deployable app and the review pipeline that gates anything entering `main`. Generated content is treated as an untrusted change, never auto-merged. The interesting part is the guardrails between the model and `main`:

- **Two-stage review** ([`card-review.yml`](.github/workflows/card-review.yml)). Deterministic Python check first ([`review_new_cards.py`](tools/review_new_cards.py)) — frontmatter shape, slugs, duplicate ids and duplicate questions vs. base ref, length floors. LLM judge second ([`review_new_cards_llm.py`](tools/review_new_cards_llm.py)) — only after the cheap checks pass. The LLM is never the sole gate.
- **Treat model I/O as untrusted.** System prompt explicitly frames card fields as data, not instructions (prompt-injection defense). Response uses `response_format: json_object` with a fixed schema; unknown verdicts collapse to `warn`, not `pass`; payload sets `"store": false`.
- **Leak detector for raw LLM artifacts.** Deterministic stage fails on source-log markers (`### pytanie`, `as an ai`, `jako model`, etc.) that should never reach a published card.
- **Bounded cost / blast radius.** Per-PR caps: `MAX_LLM_REVIEW_CARDS=5`, `MAX_LLM_CARD_CHARS=4500`, `MAX_LLM_COMPLETION_TOKENS=2000`, `MAX_LLM_SUGGESTED_ANSWER_CHARS=6000`.
- **Provider portability.** OpenAI-compatible; works against OpenAI directly or a LiteLLM gateway. With no credentials, the LLM step exits cleanly and the deterministic stage still runs.
- **Secret hygiene.** Output redaction via regex for OpenAI/GitHub/AWS key shapes ([`output_safety.py`](tools/output_safety.py)) before anything lands in a PR comment. LLM step and PR-write step gated on `head.repo == base.repo` so fork PRs never see secrets or `GITHUB_TOKEN` write scope.
- **Idempotent PR comment.** Marker-based update ([`post_pr_comment.py`](tools/post_pr_comment.py)) — re-runs edit the existing comment instead of stacking.

## License

[MIT](LICENSE).
