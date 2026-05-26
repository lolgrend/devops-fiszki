---
id: terraform.ci-credentials-oidc
title: CI credentials with OIDC
technologies: [terraform]
areas: [cicd]
tags: [ci, oidc, aws, credentials, iam]
difficulty: senior
question: How should Terraform authenticate to AWS in CI, and why are long-lived access keys an anti-pattern?
---

Long-lived `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` values in CI secrets are risky:

- Stolen once means usable for a long time.
- Rotation is manual and often forgotten.
- Audit trails are weaker.
- Logs and runner environments can leak secrets.

Prefer OIDC. The CI system issues a short-lived identity token, and AWS validates it with `sts:AssumeRoleWithWebIdentity`.

Benefits:

- No static cloud secret in CI.
- Short-lived credentials.
- Per-environment roles.
- Better audit trail through role session names and trust policy conditions.

Trust policies should restrict both `aud` and `sub`, for example to a specific repository, branch, or protected environment.
