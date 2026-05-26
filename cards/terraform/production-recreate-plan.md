---
id: terraform.production-recreate-plan
title: Production Recreate Plan
technologies: [terraform, aws]
areas: [plan, state, drift, providers, modules]
tags: [replace, drift, state, rds, ci]
difficulty: mid
question: How do you investigate and safely handle a Terraform plan that wants to replace production resources after a seemingly tag-only change?
---

First, stop the merge request and treat the plan as suspicious: tag updates should usually be in-place, so a `-/+` on production resources means Terraform sees a force-replace change or state mismatch.

### 1) Investigate why replacement is happening
- Compare the Git diff with what is in the plan.
- Render and inspect the plan to see the exact attributes causing replacement.
- Check current live state and addresses.
- Look for changes in module/provider versions, drift, bad import, or moved resource addresses.

### 2) Commands to run
```sh
terraform plan
terraform plan -out=tfplan
terraform show tfplan
git diff
terraform state list | grep prod
terraform state show aws_db_instance.prod
terraform state show aws_lb_target_group.api_tg
```

### 3) How to decide the root cause
- **Code change:** an immutable argument changed, e.g. `name`, `identifier`, `vpc_id`, `subnet_group`, `target_type`, `protocol`, `port`.
- **Provider/module change:** version bump changed diff behavior or defaults.
- **Drift:** AWS config no longer matches state.
- **Import/state issue:** resource exists but was imported incorrectly or not at the right address.
- **Refactor/state move:** resource moved in code but state was not moved with `terraform state mv`.

### 4) When to use key commands
- `terraform plan`: validate the intended change and see if it forces replacement.
- `terraform state show`: inspect the exact tracked attributes of a resource.
- `terraform state list`: find resource addresses currently in state.
- `terraform providers lock`: pin provider versions/checksums to avoid surprise behavior.
- `terraform import`: bring an existing real resource under Terraform control.
- `terraform state mv`: move state to a new resource address during refactors.

### 5) Prevent accidental destruction of prod DB
- Add `lifecycle { prevent_destroy = true }` on the DB.
- Enable RDS `deletion_protection = true`.
- Require a manual approval step for production applies.
- Block destroy/replace of RDS with CI policy checks.
- Require backup/snapshot and explicit approval before any replacement.

### 6) Harden repo and pipeline
- Pin provider and module versions.
- Require review of the saved plan artifact (`terraform plan -out=tfplan` + `terraform show tfplan`).
- Fail CI on any unexpected destroy/replace in production.
- Review moved/imported resources during refactors.
- Keep state and code aligned after renames or module restructuring.
