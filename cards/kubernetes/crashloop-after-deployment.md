---
id: kubernetes.crashloop-after-deployment
title: CrashLoopBackOff after deployment
technologies: [kubernetes]
areas: [troubleshooting]
tags: [crashloopbackoff, rollback, probes, logs, deployments]
difficulty: senior
question: A new Kubernetes deployment succeeds, then pods enter CrashLoopBackOff. How do you diagnose and decide on rollback?
---

First preserve evidence and find the termination reason. `CrashLoopBackOff` means Kubernetes keeps restarting a container that exits or fails probes.

Useful commands:

```bash
kubectl get deploy,rs,pods
kubectl get pods -o wide
kubectl logs <pod> --previous
kubectl logs <pod>
kubectl describe pod <pod>
kubectl describe deploy api-service
kubectl get pod <pod> -o yaml
kubectl top pod
```

Check:

- Application logs and exit code.
- `OOMKilled` or CPU throttling.
- Probe failures.
- Missing or changed ConfigMaps and Secrets.
- Wrong image tag, command, args, or environment variables.
- Broken dependency such as database, DNS, or external API.
- Whether failures are isolated to one node.

Rollback when production impact continues, the issue correlates with the deployment, and there is no quick low-risk fix. Prefer the normal CI/CD rollback path if it is fast. For immediate mitigation:

```bash
kubectl rollout undo deployment/api-service
kubectl rollout status deployment/api-service
```

Improve the deployment process with realistic readiness checks, startup probes for slow boot, pre-prod smoke tests, canaries or progressive delivery, and pipeline gates that fail when the rollout becomes unhealthy.
