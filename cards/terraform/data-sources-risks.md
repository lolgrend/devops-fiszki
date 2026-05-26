---
id: terraform.data-sources-risks
title: Risks of overusing data sources
technologies: [terraform]
areas: [advanced]
tags: [data-sources, providers, performance, coupling]
difficulty: senior
question: What is dangerous about overusing Terraform data sources?
---

A data source is a read-time API call during plan or apply.

Risks:

- Plans become slower because every data source calls provider APIs.
- API rate limits become more likely.
- `most_recent = true` can create surprise replacements when a new AMI appears.
- Plans become tightly coupled to infrastructure outside the current state.
- Cross-account data sources add authentication overhead.
- Cycles become easier to create when modules read each other's outputs indirectly.

Example risk:

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
}
```

For stable infrastructure, pin important values through variables, outputs, or a controlled artifact pipeline. Use data sources intentionally, not as a global lookup habit.
