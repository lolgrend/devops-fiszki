---
id: terraform.dynamic-blocks
title: Dynamic blocks
technologies: [terraform]
areas: [advanced]
tags: [dynamic-blocks, modules, hcl, readability]
difficulty: senior
question: When are dynamic blocks necessary, and when are they over-engineering?
---

`dynamic` generates repeated nested blocks from a collection.

```hcl
resource "aws_security_group" "app" {
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

Use dynamic blocks when the number of nested blocks is genuinely variable, especially in reusable modules.

Avoid them when configuration is static and clearer when written directly. Two known ingress rules are usually easier to review as two explicit blocks.

Rule of thumb: if the abstraction reduces real duplication without hiding intent, use it. If it makes the reader simulate HCL in their head, it is probably too clever.
