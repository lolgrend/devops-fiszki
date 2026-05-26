---
id: kubernetes.scale-up-timeouts-debugging
title: Scale-up Timeout Debugging
technologies: [kubernetes]
areas: [scaling, troubleshooting]
tags: [timeouts, 5xx, endpoints, resources, hpa]
difficulty: mid
question: How do you diagnose intermittent timeouts and 5xx errors that appear only after a Kubernetes Deployment is scaled up?
---

Start by verifying whether the failures come from **new replicas not becoming truly ready**, **node/resource saturation**, or **downstream dependencies** that cannot handle the higher concurrency. Do not keep increasing replicas until you know which of those is happening.

1. **Check pod status, restarts, and events**
   Look for `CrashLoopBackOff`, `OOMKilled`, failed probes, image pull issues, or pods stuck in `Pending`.

2. **Confirm new replicas are actually Ready before they receive traffic**
   Review readiness probes, startup probes, and app startup time. A common scale-up problem is that pods start slowly or pass readiness too early, then receive traffic and return 5xx/timeouts.

3. **Check whether the cluster has capacity for the extra replicas**
   If scaled pods are pending, unschedulable, or causing node CPU/memory pressure, requests may queue or fail. If using Cluster Autoscaler, verify whether nodes were added in time.

4. **Check per-pod logs and compare old vs new replicas**
   Correlate errors to specific pods. If only newly created pods fail, suspect initialization, config, warm-up, or dependency connection storms.

5. **Check resource usage**
   Use `kubectl top` to see CPU/memory usage on pods and nodes. For CPU throttling, use container/runtime or Prometheus metrics rather than `kubectl top` alone.

6. **Verify Service routing to only Ready pods**
   Ensure the Service is sending traffic only to pods that are marked Ready. Inspect endpoints/EndpointSlices and confirm readiness probe behavior is correct.

7. **Check downstream systems and connection scaling effects**
   Scaling from 2 to 8 replicas can multiply DB connections, cache clients, queue consumers, or external API calls. That can cause timeouts even when Kubernetes itself looks healthy.

8. **Consider rollout and warm-up effects**
   During scale-up or rolling updates, `maxSurge`, cold caches, JIT/runtime warm-up, or expensive startup tasks can temporarily increase latency and 5xx rates.

Useful commands:
```sh
kubectl get pods -o wide
kubectl describe pod <pod>
kubectl logs <pod> --since=30m
kubectl top pods
kubectl top nodes
kubectl get endpoints <service>
kubectl get endpointslice -l kubernetes.io/service-name=<service>
kubectl describe deployment <deployment>
```

What to conclude:

- **Only new pods fail**: investigate readiness/startup probes, app initialization, config, or dependency connection spikes.
- **Pods are Pending or nodes are saturated**: cluster capacity or scheduling is the bottleneck.
- **All pods degrade after scaling**: likely a shared dependency such as a DB, cache, queue, or external API.
- **Pods are in Service endpoints before they can serve traffic**: fix readiness/startup probe behavior first.

Use HPA only when the workload has a valid scaling signal and the cluster plus dependencies can absorb more replicas. More pods can make timeouts worse if the real bottleneck is a shared resource or external limit.
