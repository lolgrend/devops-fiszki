---
id: aws.ecs-fargate-safe-deployments
title: ECS Fargate deployment redesign
technologies: [aws, ecs, fargate, alb, ecr, terraform, gitlab-ci, secrets-manager, ssm, codedeploy]
areas: [deployment, release-management, secrets, health-checks, rollback]
tags: [ecs, fargate, terraform, gitlab, rollback, secrets]
difficulty: senior
question: How would you design an AWS ECS Fargate deployment behind an ALB so releases are deterministic, rollback is safe, secrets are handled correctly, and Terraform is not misused for app rollouts?
---

1. **Separate infrastructure from application delivery.** Use Terraform for long-lived resources only: ECS cluster/service, ALB, target groups, IAM, autoscaling, log groups, deployment controller, and secret *references*. Do **not** run `terraform apply` on every app release.

2. **Deploy the app by creating a new ECS task definition revision** that points to an **immutable image** in ECR, ideally by digest, or at least by commit SHA tag. `aws ecs update-service --force-new-deployment` alone is not enough, because it only redeploys the currently configured task definition.

```bash
IMAGE="123456789012.dkr.ecr.eu-west-1.amazonaws.com/app:$CI_COMMIT_SHA"
docker build -t "$IMAGE" .
docker push "$IMAGE"

aws ecs register-task-definition --cli-input-json file://rendered-taskdef.json
aws ecs update-service --cluster prod --service api --task-definition api:123
```

3. **Rollback should be deterministic.** Store the mapping `environment -> task definition revision -> image digest -> Git SHA`. Roll back by updating the service to the previous known-good task definition revision, or use ECS deployment circuit breaker / CodeDeploy automatic rollback.

4. **Secrets**: keep runtime secrets in **AWS Secrets Manager** or **SSM Parameter Store** and inject them through the ECS task definition `secrets` field. The **ECS agent** resolves those references at task startup using the **task execution role**, so that role needs `secretsmanager:GetSecretValue` / `ssm:GetParameters` and the relevant KMS decrypt permissions. The **task role** is different: it is the identity the application inside the container assumes at runtime to call AWS APIs (S3, DynamoDB, etc.). Do not collapse the two — granting app-runtime permissions on the execution role is a common antipattern. Avoid plaintext secrets in Terraform state, plan output, or GitLab variables. Prefer GitLab **OIDC + AssumeRole** over long-lived AWS keys.

5. **Health and gradual rollout**: use ALB target group health checks, `healthCheckGracePeriodSeconds`, `minimumHealthyPercent`, `maximumPercent`, ECS deployment circuit breaker, and CloudWatch alarms. For traffic shifting use **CodeDeploy blue/green** with linear or canary modes — note that canary/linear is a CodeDeploy feature, native ECS rolling deployments don't support it. Use lightweight `/healthz` and `/readyz`; keep deeper validation in post-deploy smoke tests.

6. **Pipeline shape**: `test -> build -> deploy_dev -> deploy_staging -> smoke_tests -> deploy_prod(manual/approved) -> rollback`. Promote the **same built image** across environments, serialize prod deploys with a lock such as GitLab `resource_group`, and keep infra and app rollout in separate pipelines or execution paths.

7. **Residual risks**: backward-incompatible DB migrations, shallow health checks missing business failures, secret rotation issues, external dependency outages, and Terraform drift or manual console changes.
