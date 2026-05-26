---
id: kubernetes.hpa-troubleshooting
title: HPA troubleshooting when latency rises
technologies: [kubernetes]
areas: [autoscaling]
tags: [hpa, metrics, requests, latency, troubleshooting]
difficulty: senior
question: HPA does not scale during high latency, node CPU is high, but app CPU in HPA is low. What do you check?
---

Start by separating node pressure from the metric HPA actually uses. HPA CPU utilization is based on pod CPU usage divided by container CPU requests, not node CPU.

Check HPA status and metrics:

```bash
kubectl get hpa
kubectl describe hpa <name>
kubectl top pods
kubectl top nodes
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods
kubectl describe deploy <deployment>
```

Verify:

- Metrics Server is working.
- The target Deployment is correct.
- Containers have realistic `resources.requests.cpu`.
- HPA conditions do not show missing metrics or `FailedGetScale`.
- The bottleneck is not memory, I/O, database connections, queue depth, external APIs, or another workload consuming node CPU.

If CPU is the wrong signal, scaling on CPU will not help. For web APIs and workers, better signals may be request rate, latency, queue depth, or active connections through custom or external metrics.

Immediate mitigation can be manual replica scaling or increasing `minReplicas`. Add nodes only if cluster capacity is actually constrained.

If sidecars dilute pod-level CPU utilization, consider `ContainerResource` metrics where supported so HPA scales from the application container instead of the whole pod.
