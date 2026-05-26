---
id: terraform.opentofu-license-differences
title: Terraform licensing and OpenTofu
technologies: [terraform]
areas: [opentofu]
tags: [opentofu, licensing, hashicorp, state-encryption]
difficulty: senior
question: What happened to Terraform licensing, why did OpenTofu appear, and what practical differences matter?
---

In 2023 HashiCorp changed Terraform from MPL 2.0 to BUSL 1.1. BUSL is not an OSI-approved open source license and restricts some competitive commercial use cases.

OpenTofu forked from the last MPL-licensed Terraform codebase and moved under the Linux Foundation.

Practical points:

- OpenTofu aims to be a drop-in replacement for most Terraform workflows.
- Commands are `tofu init`, `tofu plan`, and `tofu apply`.
- OpenTofu adds features such as native state encryption.
- Terraform has HashiCorp-specific ecosystem features such as HCP Terraform and Sentinel.
- Registry behavior and provider resolution should be tested before migration.

For new projects, OpenTofu may be a reasonable default if the organization wants an open governance model. Existing Terraform users should test providers, state backends, CI, and policy tooling before switching.
