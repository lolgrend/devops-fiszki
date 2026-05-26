---
id: terraform.force-replacement-analysis
title: Terraform force replacement analysis
technologies: [terraform, aws]
areas: [planning, state, change-management]
tags: [forcenew, drift, state-mv, import, prevent-destroy, rollout]
difficulty: senior
question: How do you analyze a Terraform plan that wants to recreate production resources, decide whether it is drift, refactor, or a real infrastructure change, and roll it out safely?
---

1. **Immediate safety**
   Do **not** apply blindly. Treat the PR description as untrusted and review the saved plan. Here, this is **not** a tag-only change: `identifier`, security group `name`, and target group `port` are **ForceNew** attributes, so Terraform plans replacement.

2. **Investigation**
   Compare **three sources**: Git diff, Terraform state, and the real cloud resource/API. Use `terraform plan` for normal analysis, or `terraform plan -refresh-only` to detect drift without proposing config changes. Distinguish:
   - **Drift**: infra changed outside Terraform
   - **Refactor**: resource address changed in code, physical object should stay the same
   - **Real change**: physical attribute changed, replacement may be expected

3. **Decision criteria**
   - Use `terraform state mv` when only the **resource address** changed, e.g. rename `aws_db_instance.prod` to `aws_db_instance.main`
   - Use `terraform import` when the resource already exists but is **not in state**
   - Use `lifecycle { prevent_destroy = true }` on critical resources such as production databases
   - Use `ignore_changes` only for intentionally external/noisy fields, **not** to hide dangerous drift

4. **Critical resources and rollout**
   Never replace production databases, VPCs, subnets, NAT gateways, load balancers, target groups, EKS clusters, or critical IAM roles "in the dark". If replacement is truly required, do it as a migration: create new resource, attach dependencies, shift traffic gradually, validate health, keep rollback, then retire the old one.

```bash
terraform plan
terraform plan -refresh-only
terraform state mv aws_db_instance.prod aws_db_instance.main
terraform import aws_security_group.app sg-0123456789abcdef0
```

5. **Prevention and senior PR review**
   Require reviewed plan artifacts, manual approval for production apply, protected branches/environments, state locking, and policy checks that block destructive changes unless explicitly approved. In review, check ForceNew fields, blast radius, dependency chains, rollback path, and whether the change is drift, refactor, or a real design change.
