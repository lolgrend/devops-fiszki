---
id: ci-cd.branching-strategies
title: Branching strategy selection
technologies: [git, github, gitlab]
areas: [version-control, release-management, deployment]
tags: [git-flow, github-flow, gitlab-flow, trunk-based, branching]
difficulty: mid
question: How do Git Flow, GitHub Flow, GitLab Flow, and trunk-based development differ, and when should you choose each strategy?
---

Choose based on **release model**, **branch lifetime**, and **deployment maturity**.

- **Git Flow**: long-lived `main` and `develop`; `feature/*` branch from `develop`; `release/*` for stabilization; `hotfix/*` from `main`. Best for **versioned, discrete releases** such as mobile apps, desktop software, libraries, or firmware. Weak fit for CD because it increases merge complexity and integration delay.
- **GitHub Flow**: only one long-lived branch, `main`, which must stay deployable. Work happens on short-lived branches, then PR -> CI/review -> merge -> deploy. Best for **web/SaaS with continuous deployment**. Simple and fast, but assumes strong CI and often feature flags.
- **GitLab Flow**: GitHub Flow plus either **environment branches** (`main` -> `pre-production` -> `production`) or **release branches** (`release/X.Y`). Good when you need **auditable promotion across environments**, gated deploys, or support for older versions.
- **Trunk-based development**: developers commit directly to `main` or use branches that live less than a day; incomplete work is hidden behind feature flags. Best for **high-velocity, mature engineering organizations** with strong CI, monitoring, and fast rollback.

**Decision criteria**
1. Need formal, versioned releases? Use **Git Flow** or **GitLab Flow with release branches**.
2. Need simple continuous delivery to a single target? Use **GitHub Flow**.
3. Need controlled promotion between environments or compliance evidence? Use **GitLab Flow with environment branches**.
4. Need maximum throughput and can enforce strict engineering discipline? Use **trunk-based development**.

**Rule of thumb**: for modern web/CD, prefer **GitHub Flow** or **trunk-based**. Do not treat **Git Flow** as the default; it is mainly useful when the release itself is a first-class process.
