---
id: kubernetes.rollout-status-vs-traffic-readiness
title: Rollout Status and Traffic Readiness
technologies: [kubernetes, gitlab-ci, kubectl]
areas: [readiness, rollout, service-discovery]
tags: [readinessprobe, livenessprobe, startupprobe, service, ingress]
difficulty: mid
question: How do you diagnose a Kubernetes deployment that reports a successful rollout but users still see intermittent 503 errors?
---

Start by assuming the deployment may be **Ready for Kubernetes** but not truly ready for traffic. `kubectl rollout status` only confirms the Deployment reached the desired replica count and the pods became Ready; it does **not** prove the app is functionally healthy.

1. **Immediate check:** verify whether the Service still has valid backends.
   - `kubectl get svc`
   - `kubectl get endpoints api-service`
   - `kubectl get endpointslices`
   - `kubectl describe svc api-service`

2. **Investigate readiness vs runtime health:**
   - `Running` means the container process exists.
   - `Ready` means the pod can receive traffic according to `readinessProbe`.
   - If the probe is too shallow, pods can become Ready before the app is actually usable.
   - Use `livenessProbe` for process recovery and `startupProbe` for slow startups so readiness is not evaluated too early.

3. **Look for selector/label mismatch:**
   - Compare Service selector with pod labels.
   - `kubectl get pods --show-labels`
   - A mismatch can cause some pods to be excluded from endpoints, producing intermittent 503s.

4. **Validate the rollout beyond status:**
   - Run smoke tests after deploy against a real endpoint, not only `kubectl rollout status`.
   - Check the Ingress path, Service routing, and backend endpoint stability.
   - Add checks for business-critical endpoints, not just `/health`.

5. **Rollback criteria:**
   - If 503s continue and correlate with the new deployment, rollback quickly.
   - Command: `kubectl rollout undo deployment/api-service`

6. **Prevention:**
   - Make readiness checks reflect real user-facing readiness.
   - Add `startupProbe` for long initialization.
   - Add post-deploy smoke tests and alerting on 5xx/error rate so the pipeline fails on real traffic issues, not only on Kubernetes rollout success.
