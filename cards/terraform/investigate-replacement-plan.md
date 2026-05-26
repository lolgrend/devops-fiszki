---
id: terraform.investigate-replacement-plan
title: Investigating unexpected replacement plans
technologies: [terraform, aws]
areas: [cicd]
tags: [plan, replacement, prevent-destroy, providers, drift]
difficulty: senior
question: A tiny tag change produces a Terraform plan with production destroys and replacements. How do you investigate?
---

Stop the merge request until the replacement reason is understood. Tag changes are usually in-place, so `-/+` replacements are a red flag.

Read the plan for `forces replacement` and identify the exact attributes:

```bash
terraform plan -out=tfplan
terraform show tfplan
terraform show -json tfplan > tfplan.json
terraform state show aws_db_instance.prod
terraform state show aws_lb_target_group.api_tg
terraform state list
git diff
```

Check likely causes:

- An immutable argument changed, such as RDS `identifier`, engine, subnet group, target group port, protocol, target type, or VPC ID.
- The provider or module version changed.
- There is drift in AWS.
- The resource was imported into the wrong address or with incomplete HCL.
- A module refactor changed resource addresses without a `moved` block or `terraform state mv`.

Use `terraform providers lock` when provider lock files are missing or inconsistent across platforms. Use `terraform import` when a real resource exists but is not correctly in state. Use `terraform state mv` or `moved` blocks when the resource address changed but the object should stay the same.

Production databases need multiple guards:

- `lifecycle { prevent_destroy = true }`
- Provider-native deletion protection, such as RDS `deletion_protection = true`
- Manual approval for prod
- CI policy that blocks destructive plans unless explicitly reviewed
- Backup or snapshot strategy before risky changes
