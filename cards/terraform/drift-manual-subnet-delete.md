---
id: terraform.drift-manual-subnet-delete
title: Terraform Drift After Subnet Deletion
technologies: [terraform, aws]
areas: [drift, state]
tags: [drift, subnet, cloudtrail, production]
difficulty: mid
question: How should you respond when Terraform fails with InvalidSubnetID.NotFound because a subnet was manually deleted in AWS, and what should you check before applying a fix?
---

1. **Freeze deployments** that touch the affected VPC/subnet path to avoid making the outage wider.
2. **Investigate drift** with `terraform plan`, `terraform state list`, and `terraform state show aws_subnet.xxx`. Confirm the subnet is gone from AWS, not just from Terraform.
3. **Check dependencies before apply**: route table associations, NAT routes, ASG subnet lists, target groups, ENIs, EKS node groups, and RDS subnet groups. These may also need update or recreate.
4. **Apply the corrected Terraform** to recreate the subnet with the same CIDR/tags if needed, but expect a **new subnet ID**; a deleted subnet cannot be restored 1:1.

```sh
terraform plan
terraform state list
terraform state show aws_subnet.xxx
aws ec2 describe-subnets --subnet-ids subnet-...
aws cloudtrail lookup-events
```

5. **Prevent recurrence** with IAM/SCP deny for manual subnet deletion in prod, break-glass access only, CloudTrail alerts, AWS Config, and drift-detection in the pipeline.
