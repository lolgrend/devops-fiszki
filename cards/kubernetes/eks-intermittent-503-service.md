---
id: kubernetes.eks-intermittent-503-service
title: EKS intermittent 503 troubleshooting
technologies: [kubernetes, eks, aws, coredns, kube-proxy]
areas: [networking, services, debugging, readiness]
tags: [eks, service, endpoints, readiness, networkpolicy, 503]
difficulty: senior
question: How would you troubleshoot intermittent HTTP 503s for an EKS ClusterIP Service when Pods are Running and Ready, but clients from another namespace fail via the internal DNS name?
---

1. **Immediate mitigation / safety**
   - Confirm whether the `503` comes from the app, sidecar, or another proxy; a `ClusterIP` Service is not an HTTP proxy.
   - If the issue started after a rollout, prefer `kubectl rollout undo deployment/orders-api -n orders`.
   - If one bad replica is suspected, remove it as an emergency action or temporarily scale up replicas to restore capacity.

2. **Investigation**
   - Check whether Service backends are stable over time:

```bash
kubectl describe svc -n orders orders-api
kubectl get endpoints -n orders orders-api -o wide
kubectl get endpointslice -n orders -l kubernetes.io/service-name=orders-api -o wide
watch -n 1 'kubectl get endpoints -n orders orders-api -o wide'
```

   - If endpoints are empty or flapping, inspect selectors, labels, readiness, restarts, rollout state, and events:

```bash
kubectl get pods -n orders --show-labels
kubectl get pods -n orders -o wide
kubectl describe deploy -n orders orders-api
kubectl get rs -n orders
kubectl get events -n orders --sort-by=.lastTimestamp
```

   - Verify `targetPort` matches the actual listening port:

```bash
kubectl get svc -n orders orders-api -o yaml
kubectl get deploy -n orders orders-api -o yaml
kubectl exec -n orders deploy/orders-api -- ss -lntp
```

   - Test from the **client namespace** to separate DNS/connectivity from backend behavior:

```bash
kubectl run tmp-debug -n <client-namespace> --rm -it --image=curlimages/curl -- sh
nslookup orders-api.orders.svc.cluster.local
curl -v http://orders-api.orders.svc.cluster.local
```

3. **Decision criteria**
   - **Endpoints unstable**: focus on readiness probe quality, startup/warm-up, restarts, graceful termination, resource pressure, and rollout settings.
   - **Endpoints stable + DNS works + port correct**: check NetworkPolicy, namespace egress/ingress, CoreDNS reachability, kube-proxy, AWS VPC CNI, and whether only one pod/node/AZ is failing.
   - **HTTP reaches pods but still 503**: likely application-level causes such as DB/cache/external API failures, connection pool exhaustion, or a shallow readiness probe.

4. **EKS metrics/logs**

```bash
kubectl top pods -n orders
kubectl top nodes
kubectl logs -n orders deploy/orders-api --since=30m
kubectl logs -n kube-system deploy/coredns --since=30m
kubectl logs -n kube-system daemonset/aws-node --since=30m
kubectl logs -n kube-system daemonset/kube-proxy --since=30m
```

   Look for 5xx by pod, latency by pod, readiness transitions, restarts, OOMKills, CPU throttling, node pressure, CoreDNS errors, and CNI/IP allocation issues.

5. **Prevention**
   - Make readiness probe reflect real business readiness, not just process startup.
   - Review `startupProbe`, `preStop`, `terminationGracePeriodSeconds`, and rolling update settings such as `maxUnavailable`.
   - Monitor per-pod 5xx, endpoint changes, and rollout health. Mental model: `Running != Ready != present in endpoints != able to serve traffic`.
