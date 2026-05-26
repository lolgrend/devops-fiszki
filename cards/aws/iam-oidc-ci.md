---
id: aws.iam-oidc-ci
title: AWS IAM OIDC for CI
technologies: [aws]
areas: [identity]
tags: [iam, oidc, ci, sts]
difficulty: senior
question: How does AWS OIDC federation remove the need for static CI access keys?
---

The CI provider issues a signed OIDC token for the job. AWS IAM trusts that issuer and allows the job to call `sts:AssumeRoleWithWebIdentity`.

The IAM role trust policy should restrict:

- The OIDC provider.
- The expected audience.
- The repository, branch, tag, or environment encoded in the token subject.

The job receives temporary AWS credentials instead of long-lived access keys.

In GitHub Actions this also requires explicit `id-token: write` permission for the job or workflow that needs to request an OIDC token.

Benefits:

- No static cloud secret stored in CI.
- Short credential lifetime.
- Better audit trail through role sessions.
- Separate roles for dev, staging, and production.

This is a good default for Terraform pipelines, deployment jobs, and automation that runs from GitHub Actions, GitLab CI, or similar systems.
