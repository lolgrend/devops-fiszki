---
id: terraform.import-existing-resource
title: Importing existing resources
technologies: [terraform]
areas: [state]
tags: [import, state, brownfield, refactoring]
difficulty: senior
question: How do you bring a manually created AWS resource under Terraform without recreating it?
---

Prefer declarative import blocks in modern Terraform.

```hcl
import {
  to = aws_s3_bucket.legacy
  id = "my-existing-bucket"
}

resource "aws_s3_bucket" "legacy" {
  bucket = "my-existing-bucket"
}
```

Then run:

```bash
terraform plan -generate-config-out=generated.tf
```

This gives you reviewable code and a plan that shows exactly what will be imported.

The older `terraform import` CLI command works, but it is imperative and easy to forget in Git history:

```bash
terraform import aws_s3_bucket.legacy my-existing-bucket
```

If you import into state but never add matching HCL, a later plan can become confusing or dangerous.
