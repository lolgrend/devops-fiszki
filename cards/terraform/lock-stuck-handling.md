---
id: terraform.lock-stuck-handling
title: Terraform Lock Handling
technologies: [terraform, gitlab, aws, dynamodb]
areas: [state, locking, pipeline]
tags: [force-unlock, resource-group, dynamodb, plan]
difficulty: mid
question: How do you safely handle a Terraform state lock that appears to be stuck in a CI/CD pipeline?
---

1. **Immediate mitigation:** freeze all pipelines that can touch the same state/environment. Make sure no Terraform job is still running before doing anything destructive.
2. **Investigate the lock:** inspect the lock metadata to identify the owning job/process, then verify whether it is still alive. Check CI job status, Terraform state operations, and cloud-side evidence such as AWS logs or CloudTrail.
3. **Read-only assessment:** run non-mutating commands to understand current state drift and partial progress:

```bash
terraform plan
terraform plan -refresh-only
terraform state list
terraform state show <resource>
```

4. **Decision criteria:** use `terraform force-unlock` only if you are certain the process that created the lock has died and will not resume. If the apply failed mid-way, confirm which resources changed and whether any import or reconciliation is needed before re-running.
5. **Prevention:** in GitLab, use `resource_group` per state/environment, separate plan from apply, require manual approval for prod, and avoid multiple pipelines managing overlapping resources. If needed, serialize retries instead of allowing concurrent applies.

Example GitLab protection:

```yaml
apply_prod:
  stage: apply
  resource_group: terraform-prod
  script:
    - terraform apply tfplan
```
