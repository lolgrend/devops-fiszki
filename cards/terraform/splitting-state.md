---
id: terraform.splitting-state
title: Splitting a monolithic state
technologies: [terraform]
areas: [state]
tags: [state, migration, remote-state, refactoring]
difficulty: senior
question: How do you safely split a large monolithic Terraform state into smaller states?
---

Start with a clear boundary, such as networking, identity, shared services, or one application domain.

Safe process:

- Back up state with `terraform state pull`.
- Create the new root module and backend.
- Move only one domain at a time.
- Review plans before and after the move.
- Keep migration windows small.

Classic state move:

```bash
terraform state mv \
  -state=old.tfstate \
  -state-out=new.tfstate \
  aws_vpc.main aws_vpc.main
```

Declarative alternatives can use `removed` blocks where supported and `import` blocks in the new root module.

Be careful with cross-state references. `terraform_remote_state` works, but it couples states. API lookups by tags can sometimes be a cleaner boundary.
