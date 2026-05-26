# DevOps Flashcards

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

This public repo contains the polished output and validation tooling. In the private workflow, structured learning notes are transformed into candidate cards, reviewed, and merged only after validation. That flow is review-first by design: generated content is treated as a candidate change, not as an automatic production update.
