---
id: kubernetes.hpa-basics
title: Horizontal Pod Autoscaler basics
technologies: [kubernetes]
areas: [autoscaling]
tags: [hpa, metrics, workloads, scaling]
difficulty: mid
question: What does the Kubernetes Horizontal Pod Autoscaler need in order to scale a deployment?
---

HPA watches metrics and changes the replica count of a scalable target such as a Deployment.

It needs:

- A target with a scale subresource, usually a Deployment.
- Metrics Server for CPU and memory metrics.
- Resource requests on containers when scaling by CPU or memory utilization.
- Sensible min and max replica counts.

Example:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

Without resource requests, CPU utilization percentages do not have a reliable baseline.
