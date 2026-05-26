---
id: aws.ecs-fargate-safe-gitlab-deploy
title: Safer ECS Fargate deployments
technologies: [aws, ecs, fargate, gitlab-ci, terraform, ecr]
areas: [deployments, cicd, containers, observability]
tags: [ecs, task-definition, image-digest, rollback, gitlab, terraform]
difficulty: mid
question: How would you design a safe GitLab CI/CD deployment pipeline for AWS ECS Fargate so production deploys use the exact intended image and configuration, support rollback, and avoid mutable tags and what force-new-deployment flag does?
---

1. **Immediate safety**: stop deploying with only `aws ecs update-service --force-new-deployment` for image/config changes. That command reuses the **current task definition**, so ECS may restart tasks with old image references, env vars, or secrets wiring.

2. **Correct deployment flow**: build **once**, push **once**, capture the **image digest**, render a task definition with that exact digest, register a **new task definition revision**, update the service to that revision, wait for stability, then run smoke tests. Prefer digest over tags; `latest` and other mutable tags are unsafe.

3. **Promotion and rollback**: promote the **same artifact** through `dev -> stage -> prod`; do not rebuild per environment. Keep env-specific config outside the image via task definition env vars, SSM Parameter Store, or Secrets Manager. Record deployed task definition revision and image digest per environment. Roll back by updating the service to the previous known-good task definition revision.

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs update-service \
  --cluster prod-cluster \
  --service orders-api \
  --task-definition orders-api:<new-revision>
aws ecs wait services-stable --cluster prod-cluster --services orders-api

# rollback
aws ecs update-service \
  --cluster prod-cluster \
  --service orders-api \
  --task-definition orders-api:<previous-good-revision>
```

4. **Checks and ownership**: verify ECS deployment settings and health checks: `minimumHealthyPercent`, `maximumPercent`, `healthCheckGracePeriodSeconds`, ALB target health, container health checks, desired/running/pending counts, and stopped task reasons. During incidents check ECS service events, app CloudWatch logs, ALB target and ELB 5xx, target health, CPU/memory, exit code 137/OOM, and dependency failures. Use Terraform for stable infrastructure (cluster, service baseline, IAM, networking, ALB, log groups, autoscaling), but usually not for every app release. In GitLab: build once, deploy to dev, smoke test, deploy to stage, smoke test, then **manual approval** for prod; protect branches/environments and serialize prod deploys.
