---
id: terraform.prevent-destroy
title: prevent_destroy limitations
technologies: [terraform]
areas: [lifecycle]
tags: [lifecycle, safety, deletion, policy]
difficulty: senior
question: What does prevent_destroy do, and what are its limitations?
---

`prevent_destroy = true` makes Terraform fail if a plan would destroy or replace the resource.

```hcl
resource "aws_db_instance" "prod" {
  lifecycle {
    prevent_destroy = true
  }
}
```

It helps with accidental `terraform destroy` and replacement caused by force-new attributes.

It does not protect against:

- Removing the resource block from HCL, because the lifecycle rule disappears too.
- `terraform state rm`, which removes the state entry.
- Manual deletion outside Terraform.
- Cloud-side operations by another system.

For critical resources, combine Terraform lifecycle rules with policy checks and provider-native protections such as RDS deletion protection or S3 bucket policies.
