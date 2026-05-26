---
id: terraform.state-locking
title: State locking with remote backends
technologies: [terraform]
areas: [state]
tags: [state-locking, s3, dynamodb, collaboration]
difficulty: senior
question: What happens when two engineers run terraform apply against the same remote state at the same time?
---

Terraform relies on **state locking**. The first apply acquires the lock; the second one waits or fails, depending on the backend and command options.

Locking is backend-specific:

- `s3` with DynamoDB uses a DynamoDB lock table.
- Newer S3 native locking can use `use_lockfile = true`.
- `azurerm` uses blob leases.
- `local` locking is not useful for a real team.

If a lock is stale, use `terraform force-unlock LOCK_ID` only after proving that no apply is still running. Force-unlocking a live apply can corrupt state.

```hcl
terraform {
  backend "s3" {
    bucket       = "tf-state-prod"
    key          = "infra/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
    encrypt      = true
  }
}
```
