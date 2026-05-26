---
id: terraform.workspaces-vs-environments
title: Workspaces versus environment roots
technologies: [terraform]
areas: [advanced]
tags: [workspaces, environments, modules, production]
difficulty: senior
question: Dev and prod use mostly the same Terraform, but prod has extra resources such as WAF. How should you structure this?
---

Prefer separate root modules per environment when infrastructure differs meaningfully.

```text
environments/
  dev/
    main.tf
    backend.tf
  prod/
    main.tf
    backend.tf
modules/
  network/
  app/
```

Each environment has its own state, pipeline, credentials, and approval rules. Differences are explicit instead of hidden behind many conditionals.

Using the same root module with `count = var.environment == "prod" ? 1 : 0` can work for small differences, but it grows messy.

CLI workspaces are best for lightweight variants of the same code, not strong prod/dev isolation. They do not solve credentials, approvals, or large environment differences.
