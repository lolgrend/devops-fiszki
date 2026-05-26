---
id: terraform.pipeline-apply-safety
title: Safe Terraform pipelines
technologies: [terraform]
areas: [cicd]
tags: [ci, plan, apply, policy, production]
difficulty: senior
question: How do you structure a Terraform pipeline to avoid unsafe production applies?
---

Use the plan as the apply artifact. Do not run a fresh implicit plan during apply.

```yaml
plan:
  script:
    - terraform plan -out=tfplan.binary
    - terraform show -json tfplan.binary > tfplan.json
  artifacts:
    paths: [tfplan.binary, tfplan.json]

apply:
  script:
    - terraform apply tfplan.binary
  needs: [plan]
  when: manual
```

For production:

- Require manual approval.
- Use protected environments.
- Run policy-as-code checks against the JSON plan.
- Block risky destroys, public security groups, or missing required tags.
- Schedule drift detection separately with `terraform plan -detailed-exitcode`.

The key idea is that humans approve a specific reviewed plan, not whatever Terraform happens to calculate later.
