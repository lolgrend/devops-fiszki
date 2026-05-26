---
id: terraform.null-resource-local-exec
title: null_resource and local-exec smell
technologies: [terraform]
areas: [advanced]
tags: [null-resource, provisioners, idempotency, automation]
difficulty: senior
question: Why is null_resource with local-exec a code smell in most Terraform codebases?
---

`null_resource` with `local-exec` is an escape hatch. It means Terraform is tracking that a script ran, but not necessarily what the script changed.

Problems:

- It depends on the runner environment.
- It can be non-idempotent.
- `terraform plan` does not fully validate provisioner behavior.
- Failures can vary by shell, CLI version, network, or credentials.
- State says the step happened, but not what external side effects occurred.

```hcl
resource "null_resource" "wait_for_service" {
  provisioner "local-exec" {
    command = "sleep 30 && curl https://example.com/health"
  }
}
```

Better options include provider resources, a custom provider for repeated behavior, external deployment tools, `time_sleep` for simple waits, or orchestrators such as Ansible or Step Functions.
