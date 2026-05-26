---
id: terraform.deleted-subnet-drift
title: Deleted subnet drift
technologies: [terraform, aws]
areas: [state]
tags: [drift, subnet, vpc, cloudtrail, incident-response]
difficulty: senior
question: Terraform state still contains a subnet, but AWS says InvalidSubnetID.NotFound. What is the recovery path?
---

Treat this as production drift with possible dependency impact. Freeze deployments that touch the VPC, then assess what depended on the subnet.

Important correction: a deleted subnet cannot be restored with the same subnet ID. Terraform can create a new subnet with the same CIDR and tags, but it will have a new ID. Anything that referenced the old subnet ID may need to update or recreate.

Start with read-only checks:

```bash
terraform plan
terraform state show aws_subnet.app
terraform state list
aws ec2 describe-subnets --subnet-ids subnet-...
aws cloudtrail lookup-events
```

Inspect dependent resources before applying:

- Route table associations and NAT routes.
- Auto Scaling Groups and launch templates.
- Load balancer target groups and ENIs.
- EKS node groups.
- RDS subnet groups.

If Terraform code still declares the subnet, a plan should propose creating a replacement. Review the blast radius carefully because downstream resources may also change.

Prevention:

- Deny manual subnet deletion in production with IAM or SCPs.
- Use break-glass roles with audit.
- Alert on subnet deletion through CloudTrail/EventBridge.
- Run drift detection for critical networking state.
