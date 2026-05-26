---
id: terraform.module-depends-on
title: depends_on at module level
technologies: [terraform]
areas: [lifecycle]
tags: [depends-on, modules, graph, eventual-consistency]
difficulty: senior
question: What does module-level depends_on do, and why can it be necessary?
---

Since Terraform 0.13, modules can use `depends_on`.

```hcl
module "app" {
  source = "./modules/app"
  vpc_id = module.network.vpc_id

  depends_on = [module.network]
}
```

This makes Terraform treat resources in the dependent module as waiting on resources in the dependency module.

It can help with side effects that Terraform cannot infer, such as IAM propagation, provisioners, or data sources that look up resources created by another module.

The downside is reduced parallelism. It is broader than a normal dependency through an argument such as `vpc_id = module.network.vpc_id`.

Prefer explicit value dependencies when possible. Use module-level `depends_on` as a last resort for invisible or eventually consistent dependencies.
