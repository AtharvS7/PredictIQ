Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Operational Runbook: Production Deployment & Rolling Updates

This runbook specifies the step-by-step procedure for executing a zero-downtime production deployment of PredictIQ from the active `dev3` release candidate branch.

---

## 1. Pre-Deployment Verification

Execute the unified release gate to certify the commit before deploying:

```bash
# 1. Verify working directory is clean
git status

# 2. Run unified release gate
python scripts/release_gate.py
```

Ensure all 9 checks pass. Confirm that `origin/main` and `origin/dev2` remote tracking branches remain locked at their canonical baselines.

---

## 2. Database Migration Execution

Before shifting application traffic, apply any additive schema migrations to the live Neon database:

```bash
# 1. Create a safety snapshot branch in Neon
neon branches create --project-id <PROJECT_ID> --name pre-deploy-$(date +%Y%m%d%H%M)

# 2. Execute Alembic migrations from backend/
cd backend
alembic upgrade head
cd ..
```

Verify that the migration completes cleanly without locking long-running transactions.

---

## 3. Container Build & Push

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export RELEASE_TAG="2.0.0-rc.3"

# 1. Authenticate to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 2. Build multi-arch backend image
docker build --platform linux/amd64 \
  -f backend/Dockerfile \
  -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/predictiq/backend:${RELEASE_TAG} \
  -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/predictiq/backend:latest .

# 3. Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/predictiq/backend:${RELEASE_TAG}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/predictiq/backend:latest
```

---

## 4. Zero-Downtime Rolling Service Update (ECS Fargate)

```bash
# Force deployment to launch new tasks with updated image
aws ecs update-service \
  --cluster predictiq-prod \
  --service predictiq-backend \
  --force-new-deployment

# Monitor task rollout until steady state is reached
aws ecs wait services-stable \
  --cluster predictiq-prod \
  --services predictiq-backend
```

ECS launches new task containers, probes their `/api/v1/ready` endpoints, and gradually shifts traffic at the Application Load Balancer before terminating old tasks.

---

## 5. Post-Deployment Verification & Smoke Testing

```bash
# 1. Probe live readiness endpoint
curl -fsS https://api.predictiq.io/api/v1/ready | jq .

# Verify:
# - "status": "healthy"
# - "services.database": "connected"
# - "services.ml_model": "ready"
# - "capabilities.automatic_prediction": true

# 2. Run automated operations check
python scripts/check_operations.py --base-url https://api.predictiq.io --requests 50 --concurrency 5
```

---

## 6. Rollback Procedure

If readiness fails or critical errors exceed 0.5% within the first 30 minutes:

```bash
# 1. Revert ECS task definition to previous revision
aws ecs update-service \
  --cluster predictiq-prod \
  --service predictiq-backend \
  --task-definition predictiq-backend:<PREVIOUS_REVISION>

# 2. Re-invalidate CloudFront if frontend was updated
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```
