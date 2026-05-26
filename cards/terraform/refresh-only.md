---
id: terraform.refresh-only
title: Refresh-only plans
technologies: [terraform]
areas: [state]
tags: [refresh, drift, state, ci]
difficulty: senior
question: What does terraform plan -refresh-only do, and when do you use it?
---

`terraform plan -refresh-only` asks providers for the current live state and compares it with the Terraform state file. It does not plan changes from HCL to infrastructure.

Use cases:

- Detect drift caused by manual changes.
- Update state with `terraform apply -refresh-only` without changing infrastructure.
- Run scheduled drift detection in CI.

```bash
terraform plan -refresh-only -detailed-exitcode
```

Exit codes:

- `0` means no changes.
- `1` means error.
- `2` means drift was detected.

Before Terraform 0.15, `terraform refresh` was commonly used. Refresh-only plans are safer because they make the state update explicit and reviewable.
