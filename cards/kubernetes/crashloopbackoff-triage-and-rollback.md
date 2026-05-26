---
id: kubernetes.crashloopbackoff-triage-and-rollback
title: CrashLoopBackOff Triage
technologies: [kubernetes]
areas: [troubleshooting, rollbacks, deployments]
tags: [crashloopbackoff, logs, events, rollback, oomkilled]
difficulty: mid
question: How do you diagnose a Kubernetes pod in CrashLoopBackOff after a deployment, and when should you roll back safely?
---

Start by preserving evidence and checking the most recent failure cause. Inspect previous container logs and pod events, then confirm whether the restart reason is an app error, probe failure, missing config/secret, image problem, OOMKilled, or a node-specific issue.

Useful commands:

```sh
kubectl get deploy,rs,pods
kubectl describe deploy api-service
kubectl logs api-service-7c9d8f6b7c-x92kq --previous
kubectl describe pod api-service-7c9d8f6b7c-x92kq
kubectl top pod
kubectl get pod api-service-7c9d8f6b7c-x92kq -o yaml
kubectl get pods -o wide
```

Decision criteria: if the issue began right after deployment, production is affected, and the root cause is not immediately fixable, rollback early rather than waiting for repeated failures. Use `kubectl rollout undo deployment api-service` for fast mitigation, or the CI/CD pipeline if it is the standard safe path.

After recovery, improve deployment checks so the problem is caught earlier: stronger liveness/readiness probes, startup validation, config/secret verification, resource limits aligned with real usage, and staging or canary validation before full production rollout.
