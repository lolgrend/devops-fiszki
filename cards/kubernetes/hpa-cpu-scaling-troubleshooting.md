---
id: kubernetes.hpa-cpu-scaling-troubleshooting
title: HPA CPU Scaling Troubleshooting
technologies: [kubernetes, hpa, kubectl]
areas: [autoscaling, metrics]
tags: [cpu, requests, diagnostics, scaling]
difficulty: mid
question: How do you troubleshoot a Kubernetes HPA that does not scale even though traffic and node CPU are high?
---

1. **Immediate mitigation:** if latency is impacting users, manually scale replicas or raise `minReplicas`. Add nodes only if the cluster is actually out of capacity; node CPU being high does not automatically mean HPA should scale.

2. **Investigate HPA state and real usage:**
```bash
kubectl get hpa
kubectl describe hpa <name>
kubectl top pods
kubectl top nodes
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods
```
Check the `describe hpa` output for the current target, e.g. `20% / 70%`, and compare pod metrics with node metrics.

3. **Decision criteria:** HPA CPU utilization is calculated from **pod CPU usage divided by `resources.requests.cpu`**, not from node CPU. If requests are set too high, HPA will think the app is lightly loaded. If node CPU is high but app pod CPU is low, the bottleneck may be memory, I/O, DB connections, external APIs, queues, or another workload on the node.

4. **Concrete checks:** verify pod CPU requests in the deployment, then confirm whether the app is actually constrained by CPU or by another signal. For web/API workloads, CPU may be the wrong metric.

5. **Prevention:** set realistic CPU requests and consider custom metrics such as RPS, latency, queue depth, or active connections when CPU does not reflect user-facing load.
