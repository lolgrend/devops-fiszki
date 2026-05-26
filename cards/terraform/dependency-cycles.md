---
id: terraform.dependency-cycles
title: Dependency cycles
technologies: [terraform]
areas: [advanced]
tags: [dependencies, graph, security-groups, troubleshooting]
difficulty: senior
question: How do you detect and resolve Terraform dependency cycles?
---

The symptom is usually explicit:

```text
Error: Cycle: aws_security_group.app, aws_security_group.db
```

To inspect the graph:

```bash
terraform graph | dot -Tsvg > graph.svg
```

A common case is mutual security group references. The fix is to create the security groups first, then create rules as separate resources.

```hcl
resource "aws_security_group" "app" { name = "app" }
resource "aws_security_group" "db"  { name = "db" }

resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
}
```

Other cycle sources include bidirectional `depends_on`, data sources that depend on resources that depend on the data source, and IAM policies referencing each other.
