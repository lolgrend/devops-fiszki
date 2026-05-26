---
id: terraform.state-secrets
title: Secrets in Terraform state
technologies: [terraform]
areas: [state]
tags: [secrets, encryption, iam, state]
difficulty: senior
question: Terraform state contains plaintext secrets. How do you mitigate that risk?
---

First principle: Terraform state can contain secrets even when outputs are marked `sensitive = true`. Provider attributes such as database passwords, generated tokens, and private keys can still be stored in state.

Mitigations:

- Encrypt the backend at rest, for example S3 with KMS.
- Restrict backend access with strict IAM. Anyone with `s3:GetObject` on the state bucket may be able to read secrets.
- Do not commit state files. Ignore `*.tfstate*`.
- Avoid generating long-lived secrets in Terraform when possible.
- Store secrets in systems such as AWS Secrets Manager or HashiCorp Vault and reference IDs or ARNs instead of raw values.
- Consider OpenTofu state encryption when using OpenTofu.

The real boundary is backend access. Protect the state backend like a production secrets store.
