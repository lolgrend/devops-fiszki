---
id: terraform.moved-block
title: Safe refactoring with moved blocks
technologies: [terraform]
areas: [modules]
tags: [moved, modules, refactoring, state]
difficulty: senior
question: A module used in 50 places needs an internal resource renamed. How do you avoid destroy and recreate?
---

Use a `moved` block. It documents a state address refactor in code.

```hcl
resource "aws_instance" "application" {
  # ...
}

moved {
  from = aws_instance.web
  to   = aws_instance.application
}
```

The plan shows a move rather than destroy and create.

This is better than asking every consumer to run `terraform state mv` manually:

- The migration is reviewable.
- Every environment gets the same refactor.
- The change lives in Git.
- You can leave the block in place for a while and remove it later.

The same idea works for module address changes, such as moving from `module.old` to `module.new`.
