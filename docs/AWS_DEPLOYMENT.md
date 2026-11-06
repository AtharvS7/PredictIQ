# AWS Deployment Guide — Predictify

> **Version:** v3.1.6 | **Target:** Production on AWS | **Last Updated:** May 2, 2026

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                                  │
│                                                                     │
│  ┌──────────────┐     ┌───────────────────────────────────────────┐ │
│  │  Route 53    │────▶│        Application Load Balancer (ALB)    │ │
│  │  (DNS)       │     │  - SSL/TLS termination (ACM certificate)  │ │
│  └──────────────┘     │  - Path-based routing                     │ │
│                       └──────────┬───────────┬────────────────────┘ │
│                                  │           │                      │
│                        /api/*    │           │  /*                  │
│                                  ▼           ▼                      │
│  ┌─────────────────────────┐  ┌──────────────────────────────────┐ │
│  │    ECS Fargate          │  │    S3 + CloudFront               │ │
│  │    (Backend API)        │  │    (Frontend SPA)                │ │
│  │                         │  │                                  │ │
│  │  ┌───────────────────┐  │  │  ┌────────────┐  ┌───────────┐  │ │
│  │  │ Task 1 (FastAPI)  │  │  │  │ S3 Bucket  │◀─│CloudFront │  │ │
│  │  │  Port 8000        │  │  │  │ (dist/)    │  │  (CDN)    │  │ │
│  │  └───────────────────┘  │  │  └────────────┘  └───────────┘  │ │
│  │  ┌───────────────────┐  │  │                                  │ │
│  │  │ Task 2 (FastAPI)  │  │  └──────────────────────────────────┘ │
│  │  │  Port 8000        │  │                                       │
│  │  └───────────────────┘  │                                       │
│  └──────────┬──────────────┘                                       │
│             │                                                       │
│             ▼                                                       │
│  ┌───────────────────────┐  ┌─────────────────────────────────┐   │
│  │   Amazon RDS          │  │   AWS Secrets Manager           │   │
│  │   (PostgreSQL 16)     │  │   - DATABASE_URL                │   │
│  │   - Multi-AZ          │  │   - FIREBASE_SERVICE_ACCOUNT    │   │
│  │   - Auto backups      │  │   - Auto rotation               │   │
│  └───────────────────────┘  └─────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Monitoring: CloudWatch Logs + Alarms + X-Ray (APM)         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Option A: ECS Fargate (Recommended — Serverless Containers)

This is the recommended approach. No servers to manage, auto-scaling built-in, and your Dockerfiles are already ready.

### Prerequisites

- AWS Account with admin access
- AWS CLI v2 installed and configured (`aws configure`)
- Docker installed locally
- A domain name (optional, but recommended)

---

### Step 1: Create ECR Repositories (Container Registry)

```bash
# Create repositories for both images
aws ecr create-repository --repository-name predictiq/backend --region ap-south-1
aws ecr create-repository --repository-name predictiq/frontend --region ap-south-1

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 2: Build and Push Docker Images

```bash
# From project root
# Backend
docker build -f Dockerfile.backend -t predictiq/backend .
docker tag predictiq/backend:latest <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/predictiq/backend:latest
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/predictiq/backend:latest

# Frontend
docker build -f Dockerfile.frontend -t predictiq/frontend .
docker tag predictiq/frontend:latest <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/predictiq/frontend:latest
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/predictiq/frontend:latest
```

### Step 3: Store Secrets in AWS Secrets Manager

```bash
# Store database URL
aws secretsmanager create-secret \
  --name predictiq/database-url \
  --secret-string "postgresql+asyncpg://user:pass@host:5432/predictiq"

# Store Firebase service account
aws secretsmanager create-secret \
  --name predictiq/firebase-service-account \
  --secret-string file://backend/firebase-service-account.json
```

### Step 4: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name predictiq-prod --region ap-south-1
```

### Step 5: Create Task Definition

Save as `ecs-task-definition.json`:

```json
{
  "family": "predictiq-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "predictiq-backend",
      "image": "<ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/predictiq/backend:latest",
      "portMappings": [
        { "containerPort": 8000, "protocol": "tcp" }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 15
      },
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-south-1:<ACCOUNT_ID>:secret:predictiq/database-url"
        },
        {
          "name": "FIREBASE_SERVICE_ACCOUNT",
          "valueFrom": "arn:aws:secretsmanager:ap-south-1:<ACCOUNT_ID>:secret:predictiq/firebase-service-account"
        }
      ],
      "environment": [
        { "name": "ENVIRONMENT", "value": "production" },
        { "name": "CORS_ORIGINS", "value": "https://predictiq.yourdomain.com" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/predictiq-backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# Register the task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### Step 6: Create ALB + Target Group

```bash
# Create VPC, subnets, security groups (or use default VPC)
# Create ALB
aws elbv2 create-load-balancer \
  --name predictiq-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing \
  --type application

# Create target group
aws elbv2 create-target-group \
  --name predictiq-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /api/v1/health
```

### Step 7: Create ECS Service with Auto-Scaling

```bash
aws ecs create-service \
  --cluster predictiq-prod \
  --service-name predictiq-backend \
  --task-definition predictiq-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/predictiq-backend-tg/...,containerName=predictiq-backend,containerPort=8000"
```

### Step 8: Deploy Frontend to S3 + CloudFront

```bash
# Create S3 bucket for static hosting
aws s3 mb s3://predictiq-frontend-prod --region ap-south-1

# Build frontend
cd frontend && npm run build

# Upload dist to S3
aws s3 sync dist/ s3://predictiq-frontend-prod --delete

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name predictiq-frontend-prod.s3.ap-south-1.amazonaws.com \
  --default-root-object index.html
```

### Step 9: Set Up CloudWatch Monitoring

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/predictiq-backend

# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name predictiq-high-5xx \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:ap-south-1:<ACCOUNT_ID>:predictiq-alerts
```

---

## Option B: EC2 (Simpler — Traditional Server)

If you want a simpler setup for a demo/student project:

### Single EC2 Instance Setup

```bash
# 1. Launch EC2 instance (t3.medium, Ubuntu 24.04, ap-south-1)
# 2. SSH in and install Docker
sudo apt update && sudo apt install -y docker.io docker-compose-v2 nginx
sudo usermod -aG docker ubuntu

# 3. Clone repo
git clone https://github.com/AtharvS7/PredictIQ.git
cd PredictIQ

# 4. Create .env file
cp backend/.env.example backend/.env
# Edit with your actual values: DATABASE_URL, FIREBASE_SERVICE_ACCOUNT, etc.

# 5. Build and run with docker-compose
docker compose up -d --build

# 6. Set up Nginx reverse proxy
sudo cat > /etc/nginx/sites-available/predictiq << 'EOF'
server {
    listen 80;
    server_name predictiq.yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/predictiq /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 7. Add SSL with Certbot (free)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d predictiq.yourdomain.com
```

---

## CI/CD Pipeline (GitHub Actions → AWS)

Save as `.github/workflows/cd-aws.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

env:
  AWS_REGION: ap-south-1
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-south-1.amazonaws.com
  ECS_CLUSTER: predictiq-prod
  ECS_SERVICE: predictiq-backend

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push backend image
        run: |
          docker build -f Dockerfile.backend -t $ECR_REGISTRY/predictiq/backend:${{ github.sha }} .
          docker push $ECR_REGISTRY/predictiq/backend:${{ github.sha }}

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to S3
        run: aws s3 sync frontend/dist/ s3://predictiq-frontend-prod --delete

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} \
            --paths "/*"
```

---

## AWS Cost Estimate (Monthly)

### Option A: ECS Fargate (Production)

| Service | Spec | Monthly Cost |
|---------|------|:------------:|
| ECS Fargate (2 tasks) | 0.5 vCPU, 1GB RAM each | ~$30 |
| ALB | Application Load Balancer | ~$22 |
| RDS PostgreSQL | db.t3.micro, Multi-AZ | ~$28 |
| S3 | Frontend static files | ~$1 |
| CloudFront | CDN, 10GB transfer | ~$2 |
| Secrets Manager | 3 secrets | ~$1.50 |
| CloudWatch | Logs + Alarms | ~$5 |
| ACM | SSL Certificate | Free |
| **Total** | | **~$90/month** |

### Option B: EC2 (Budget)

| Service | Spec | Monthly Cost |
|---------|------|:------------:|
| EC2 | t3.medium (2 vCPU, 4GB) | ~$30 |
| Elastic IP | Static IP | Free (if attached) |
| EBS | 30GB gp3 | ~$2.50 |
| Certbot SSL | Let's Encrypt | Free |
| **Total** | | **~$33/month** |

---

## Required GitHub Secrets for CI/CD

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |
| `CLOUDFRONT_DIST_ID` | CloudFront distribution ID (for cache invalidation) |

---

## Post-Deployment Checklist

- [ ] Verify health check: `curl https://yourdomain.com/api/v1/health`
- [ ] Confirm SSL certificate is active (no mixed content)
- [ ] Test login flow end-to-end
- [ ] Create a test estimate and verify PDF export
- [ ] Set up CloudWatch alarms for 5xx errors and high latency
- [ ] Enable AWS backup for RDS (automated daily snapshots)
- [ ] Configure CloudWatch dashboard for API response times
- [ ] Run `ANALYZE=true npm run build` to verify frontend bundle sizes

---

> *Deployment guide created May 2, 2026 — Predictify v3.1.6*
> *Architecture: ECS Fargate (backend) + S3/CloudFront (frontend) + RDS PostgreSQL*
