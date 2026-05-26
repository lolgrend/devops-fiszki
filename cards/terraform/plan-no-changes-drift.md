---
id: terraform.plan-no-changes-drift
title: Drift when plan says no changes
technologies: [terraform]
areas: [lifecycle]
tags: [drift, refresh, lifecycle, providers]
difficulty: senior
question: Terraform plan says no changes, but AWS Console shows drift. Why can that happen?
---

Common causes:

- `lifecycle.ignore_changes` tells Terraform to ignore selected attributes.
- The plan was run with `-refresh=false`, so Terraform did not read the live API.
- The drift is in a computed provider field that Terraform does not plan against.
- The resource is partly managed by another system, such as an autoscaler or deployment pipeline.
- The provider has a bug or an old schema.

Start with:

```bash
terraform plan -refresh-only
```

That shows what changed outside Terraform compared with the state file. For deeper inspection, use:

```bash
terraform show -json
```

The key distinction is live infrastructure versus state versus HCL. A normal plan compares all three, but lifecycle settings and refresh behavior can hide differences.
