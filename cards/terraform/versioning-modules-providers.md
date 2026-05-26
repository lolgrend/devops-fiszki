---
id: terraform.versioning-modules-providers
title: Versioning modules and providers
technologies: [terraform]
areas: [advanced]
tags: [versioning, providers, modules, renovate]
difficulty: senior
question: How do you version Terraform modules and providers in a monorepo with many projects?
---

Control three layers.

Pin the Terraform or OpenTofu binary:

```hcl
terraform {
  required_version = "~> 1.10.0"
}
```

Pin providers and commit `.terraform.lock.hcl`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}
```

Pin reusable modules with semver tags:

```hcl
module "vpc" {
  source = "git::https://git.example.com/infra/modules.git//vpc?ref=v2.3.1"
}
```

Avoid tracking `main` for modules. Use changelogs and automated PRs, for example Renovate, to make upgrades visible and reviewable.
