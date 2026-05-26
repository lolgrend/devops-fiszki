---
id: terraform.count-vs-for-each
title: count versus for_each
technologies: [terraform]
areas: [modules]
tags: [count, for-each, refactoring, modules]
difficulty: senior
question: When does for_each save you from painful Terraform resource replacement?
---

`count` addresses resources by numeric index. `for_each` addresses resources by stable keys.

With `count`, removing an item from the middle of a list shifts indexes:

```hcl
resource "aws_s3_bucket" "bucket" {
  count  = length(var.buckets)
  bucket = var.buckets[count.index]
}
```

If `["alpha", "beta", "gamma"]` becomes `["alpha", "gamma"]`, Terraform may treat index `1` as changed from beta to gamma and recreate the wrong thing.

With `for_each`, the key is stable:

```hcl
resource "aws_s3_bucket" "bucket" {
  for_each = toset(var.buckets)
  bucket   = each.key
}
```

Removing `beta` destroys only `aws_s3_bucket.bucket["beta"]`.

Practical rule: use `count` for boolean enablement, and use `for_each` for named collections.
