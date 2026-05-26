---
id: terraform.stale-lock-recovery
title: Recovering from a stale Terraform lock
technologies: [terraform]
areas: [state]
tags: [state-locking, force-unlock, gitlab, ci, incident-response]
difficulty: senior
question: What do you do when a Terraform state lock is stuck after a failed pipeline?
---

First, stop new writes to the same state. Freeze or pause pipelines for that environment so the recovery does not race another apply.

Then inspect the lock metadata and prove the owner is gone:

- Check the failed CI job and runner status.
- Check whether another apply is still running.
- Review the backend lock record, such as DynamoDB for older S3 backends.
- Run read-only checks before changing state.

Useful commands:

```bash
terraform plan
terraform plan -refresh-only
terraform state list
terraform state show <address>
```

Use `terraform force-unlock LOCK_ID` only after confirming the process that owns the lock is dead. Force-unlocking a live apply can corrupt state.

After unlocking, re-run the failed plan/apply path or repair imports/state deliberately, then allow the next pipeline to continue.

Prevention belongs in CI:

```yaml
apply_prod:
  stage: apply
  resource_group: terraform-prod
  script:
    - terraform apply tfplan
```

Use one `resource_group` per Terraform state or environment so production applies are serialized before Terraform has to protect itself.
