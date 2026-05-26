---
id: terraform.security-group-drift
title: Security group drift after a manual change
technologies: [terraform, aws]
areas: [state]
tags: [drift, security-groups, cloudtrail, import, aws]
difficulty: senior
question: A manual AWS security group rule appears in production and Terraform wants to remove it. How do you handle it?
---

First decide whether the rule was intentional, accidental, or emergency drift. Do not blindly apply the plan just because Terraform is the source of truth.

Check context:

- Look for an incident, change ticket, tag, or Slack message.
- Use CloudTrail to find who changed the security group and when.
- Confirm whether the rule is still needed and whether it is safe.

Compare all three views: live AWS, Terraform state, and HCL.

```bash
terraform plan
terraform state show aws_security_group.app
aws ec2 describe-security-groups --group-ids sg-...
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-...
```

If the rule is temporary or unsafe, let Terraform remove it after normal review.

If the rule is required, encode it in Terraform and review it through Git. For a separately managed rule, add an `aws_vpc_security_group_ingress_rule` or equivalent resource. If the resource already exists outside Terraform, use an import block or `terraform import` so state, code, and AWS agree.

Prevention:

- Restrict production console changes with IAM or SCPs.
- Keep a break-glass path for incidents.
- Alert on security group changes with CloudTrail/EventBridge.
- Run scheduled drift detection.
