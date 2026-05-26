---
id: ci-cd.github-actions-dind-matched-paths
title: GitHub Actions DinD path mismatch
technologies: [github-actions, docker, dind]
areas: [ci, containers, runner-storage]
tags: [github-actions, dind, bind-mounts, self-hosted-runner, container-jobs]
difficulty: senior
question: Why can a self-hosted GitHub Actions runner using Docker-in-Docker fail immediately on a `container:` job step with exit code 1, and how do you fix it without removing DinD?
---

The usual cause is a **workspace path mismatch between the runner container and the DinD daemon container**. Official `actions/runner` handles `container:` jobs by creating a script under `_work/_temp`, then asking Docker to **bind-mount** `<runner_home>/_work` into the job container and execute that script from `/__w/_temp/...`.

If the Docker daemon is DinD, the bind mount is resolved from the **daemon container filesystem**, not the runner container. When the same path does not exist inside DinD, Docker mounts an empty directory, so `bash /__w/_temp/<uuid>.sh` is missing and exits almost instantly.

1. **Immediate check**: inspect `_diag/Worker_*.log` for `docker create ... -v <runner_home>/_work:/__w` followed by `docker exec ... bash /__w/_temp/<uuid>.sh` and a fast failure.
2. **Confirm** from the DinD container that `<runner_home>/_work/_temp` is missing or empty.
3. **Fix**: make `_work` visible under the **same absolute path** in both runner and DinD.

```yaml
services:
  github-dind:
    volumes:
      - ./data:/runners

  runner:
    environment:
      RUNNER_HOME: /runners/fiszki
    volumes:
      - ./data/fiszki:/runners/fiszki
```

Also make the runner use `RUNNER_HOME` consistently in entrypoint/init logic.

This differs from Gitea `act_runner`, which uses named volumes and `docker cp`, so it does not require matched host paths. **Prevention**: standardize runner home paths, document DinD path requirements, and validate `_work` visibility from the daemon during provisioning.
