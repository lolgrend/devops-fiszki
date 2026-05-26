---
id: terraform.atlantis-hcp-gitlab
title: Atlantis, HCP Terraform, and custom CI
technologies: [terraform]
areas: [cicd]
tags: [atlantis, hcp-terraform, gitlab, ci]
difficulty: senior
question: What are the tradeoffs between Atlantis, HCP Terraform, and custom GitLab CI?
---

**Atlantis** is open source, self-hosted, and pull-request driven. Engineers comment `atlantis plan` and `atlantis apply`.

Pros: strong PR workflow, control, low vendor lock-in. Cons: you operate it, add your own policy tooling, and manage state backend details.

**HCP Terraform** is managed by HashiCorp.

Pros: run history, RBAC, state management, policy features in paid tiers, drift workflows. Cons: cost, vendor lock-in, and less attractive if your organization standardizes on OpenTofu.

**Custom GitLab CI** uses the tooling you already have.

Pros: flexible, integrated with existing CI, good OIDC story, easy to add OPA or Conftest. Cons: every workflow detail is your YAML, and comment-based PR ergonomics need extra work.

The decision depends on team size, existing CI investment, budget, and willingness to operate another service.
