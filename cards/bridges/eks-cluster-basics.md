---
id: bridge.eks-cluster-basics
title: EKS as a Kubernetes and AWS boundary
technologies: [kubernetes, aws]
areas: [eks]
tags: [eks, iam, control-plane, networking]
difficulty: senior
question: Why is EKS a cross-domain topic between Kubernetes and AWS?
---

EKS combines Kubernetes APIs with AWS infrastructure and identity.

You need Kubernetes knowledge for:

- Workloads, services, ingress, scheduling, and autoscaling.
- Cluster add-ons such as CoreDNS and the VPC CNI.
- RBAC and Kubernetes service accounts.

You need AWS knowledge for:

- IAM roles and policies.
- VPC, subnets, route tables, and security groups.
- Load balancers and target groups.
- IRSA or EKS Pod Identity for pod-level AWS access.

The bridge is where production issues often live. A pod may be healthy from Kubernetes' point of view but unable to reach AWS APIs because IAM, DNS, routing, or security groups are wrong.
