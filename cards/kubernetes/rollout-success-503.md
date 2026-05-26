---
id: kubernetes.rollout-success-503
title: Rollout succeeds but users get 503
technologies: [kubernetes]
areas: [troubleshooting]
tags: [rollout, readiness, service, ingress, endpoints, rollback]
difficulty: senior
question: GitLab deploy and kubectl rollout status succeed, but users see intermittent 503s. What do you verify?
---

`Running` means the container process exists. `Ready` means Kubernetes believes the pod can receive traffic. Neither proves the application works for real users.

`kubectl rollout status` mostly checks whether the Deployment created new pods and reached available replicas. If `readinessProbe` is too shallow, rollout can succeed while the app still returns 503.

Check traffic routing:

```bash
kubectl get pods --show-labels
kubectl describe pod <pod>
kubectl describe svc api-service
kubectl get endpoints api-service
kubectl get endpointslices
kubectl describe ingress <ingress>
kubectl logs <pod>
```

Look for:

- Readiness probe that returns success before the app can serve real traffic.
- Missing `startupProbe` for slow startup.
- Liveness probe restarting healthy-but-slow pods.
- Service selector and pod label mismatch.
- EndpointSlices flapping or containing fewer endpoints than expected.
- Ingress or load balancer health checks disagreeing with Kubernetes readiness.

The pipeline should validate more than rollout status:

- Run smoke tests against the real route after deploy.
- Check a version endpoint and at least one meaningful business endpoint.
- Watch 5xx rate, latency, and endpoint count for a short window.
- Automatically rollback or require approval when health checks fail.

Rollback if user impact continues and the errors correlate with the deploy:

```bash
kubectl rollout undo deployment/api-service
```
