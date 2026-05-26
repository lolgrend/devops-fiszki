---
id: terraform.create-before-destroy
title: create_before_destroy tradeoffs
technologies: [terraform]
areas: [lifecycle]
tags: [lifecycle, replacement, downtime, quotas]
difficulty: senior
question: When is create_before_destroy essential, and when does it backfire?
---

Terraform normally destroys before creating when replacement is required. `create_before_destroy = true` changes the order.

It is useful for:

- Launch templates or similar dependencies.
- Security groups with references.
- Zero-downtime replacement when duplicate resources are allowed.
- IAM or networking transitions where both old and new must exist briefly.

It backfires when:

- The resource name must be globally unique, such as an S3 bucket.
- Running two copies is expensive, such as multi-AZ databases.
- Service quotas do not allow temporary duplication.

```hcl
resource "aws_launch_template" "web" {
  name_prefix = "web-"

  lifecycle {
    create_before_destroy = true
  }
}
```

Use `name_prefix` instead of fixed `name` where the provider supports it.
