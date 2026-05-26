---
id: terraform.provider-config-submodules
title: Provider configuration in reusable modules
technologies: [terraform]
areas: [modules]
tags: [providers, modules, aliases, aws]
difficulty: senior
question: Why is provider configuration inside reusable Terraform modules usually an anti-pattern?
---

Reusable modules should declare provider requirements, not configure providers.

Putting this inside a reusable module is a smell:

```hcl
provider "aws" {
  region = "eu-central-1"
}
```

Problems:

- Removing the module can fail because Terraform no longer has the provider configuration needed to destroy the resources.
- Multi-region and multi-account usage becomes hard to control from the root module.
- Provider version constraints can conflict with the root module.

Configure providers in the root module and pass aliases explicitly:

```hcl
provider "aws" {
  alias  = "us"
  region = "us-east-1"
}

module "us_resources" {
  source = "./modules/service"
  providers = {
    aws = aws.us
  }
}
```
