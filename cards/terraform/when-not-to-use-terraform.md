---
id: terraform.when-not-to-use-terraform
title: When not to use Terraform
technologies: [terraform]
areas: [advanced]
tags: [architecture, deployments, gitops, operations]
difficulty: senior
question: When should you avoid Terraform?
---

Terraform is strongest for long-lived infrastructure. Avoid using it as a universal automation tool.

Weak fits:

- Application deployments that need rolling updates, canaries, or GitOps loops.
- Runtime-mutated systems such as application-managed Kafka topics or database schemas.
- Fast application code updates, such as Lambda code deployment in a hot path.
- Imperative workflows such as database migrations and runbooks.
- Ad-hoc experiments where CLI commands are faster and lower ceremony.
- Very complex multi-cloud logic where a general-purpose language may be clearer.

Good Terraform targets include VPCs, clusters, databases, IAM, security groups, buckets, and other durable platform resources.

A practical split: Terraform builds the box; specialized tools manage what changes quickly inside the box.
