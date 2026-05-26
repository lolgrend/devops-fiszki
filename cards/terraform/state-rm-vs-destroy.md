---
id: terraform.state-rm-vs-destroy
title: Removing resources from state or infrastructure
technologies: [terraform]
areas: [state]
tags: [state, destroy, refactoring, safety]
difficulty: senior
question: What is the difference between terraform state rm, terraform destroy, and deleting a resource from HCL?
---

`terraform destroy` deletes real infrastructure and removes the objects from state.

`terraform state rm` removes only the state entry. The cloud resource stays alive, but Terraform no longer manages it. This is useful when taking a legacy resource out of Terraform management or moving state between modules.

Deleting a resource block from HCL is different: if the object is still in state, the next plan will propose a destroy. Applying that plan deletes the real resource.

The safe unmanaged-resource flow is:

```bash
terraform state rm aws_s3_bucket.legacy
```

Then remove the HCL. The next plan should show no changes for that resource.

The operational trap is deleting HCL and applying without reading the plan. That is how production resources disappear.
