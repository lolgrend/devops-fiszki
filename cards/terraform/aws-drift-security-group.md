---
id: terraform.aws-drift-security-group
title: AWS Security Group Drift
technologies: [terraform, aws, gitlab, cloudtrail]
areas: [drift, state, security-group]
tags: [drift, cloudtrail, plan, state, sg]
difficulty: mid
question: How should you handle Terraform drift when an AWS security group was changed manually in production?
---

First decide whether the manual change was intentional, temporary, or accidental. If it was an emergency workaround and is still needed, encode it in Terraform and review it through Git so code becomes the source of truth again. If it is unsafe or no longer required, let Terraform remove it on the next apply.

Investigate drift from three sides: AWS live configuration, Terraform state, and the repository code. Check the current state, compare it with AWS, and look for any incident or change record that explains why the rule exists.

Useful commands:
```bash
terraform plan
terraform state show aws_security_group.example
aws ec2 describe-security-groups --group-ids sg-...
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-...
```

Decision rule: accept the change only if it is still required and reviewed; otherwise remove it. To prevent repeats, restrict direct console edits with IAM, require changes through GitLab/Terraform pipelines, and keep CloudTrail plus alerting for manual production changes.
