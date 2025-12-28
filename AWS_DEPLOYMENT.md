# AWS Container Deployment Guide for PsychBot

This guide walks you through deploying PsychBot to AWS as a containerized application with proper credential management.

## Overview

The deployment consists of two containers:
1. **Ollama** - LLM service running llama3:8b model
2. **PsychBot** - FastAPI application with RAG system

## Prerequisites

- AWS CLI installed and configured
- Docker installed locally
- AWS account with appropriate permissions
- Your `credentials.json` file for Google Calendar
- Your SendGrid API key

---

## Step 1: Test Locally with Docker Compose

Before deploying to AWS, test that everything works locally:

```bash
# Create a .env file with your credentials
cat > .env << 'EOF'
SENDGRID_API_KEY=your-sendgrid-api-key-here
# For local testing, we'll use the volume-mounted credentials.json file
EOF

# Make sure credentials.json is in the project root

# Start both services
docker-compose up --build

# Wait for Ollama to download the model (first time ~5GB, takes a few minutes)
# Once you see "uvicorn running on http://0.0.0.0:9000", test the API:

# Open another terminal and test:
curl http://localhost:9000/docs

# Test a chat message:
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you offer?"}'
```

If everything works locally, proceed to AWS deployment.

---

## Step 2: Set Up AWS Secrets Manager

Store your sensitive credentials securely in AWS Secrets Manager:

```bash
# 1. Store Google Calendar credentials
# First, read your credentials.json content
GOOGLE_CREDS=$(cat credentials.json)

# Create the secret in AWS Secrets Manager
aws secretsmanager create-secret \
    --name psychbot/google-credentials \
    --description "Google Calendar API credentials for PsychBot" \
    --secret-string "$GOOGLE_CREDS" \
    --region us-east-1

# 2. Store SendGrid API key
aws secretsmanager create-secret \
    --name psychbot/sendgrid-api-key \
    --description "SendGrid API key for PsychBot email" \
    --secret-string "your-sendgrid-api-key-here" \
    --region us-east-1
```

Note the ARNs returned - you'll need them later:
- `arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:psychbot/google-credentials-XXXXX`
- `arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:psychbot/sendgrid-api-key-XXXXX`

---

## Step 3: Create Amazon ECR Repositories

```bash
# Create ECR repository for PsychBot
aws ecr create-repository \
    --repository-name psychbot \
    --region us-east-1

# Create ECR repository for Ollama (optional, can use Docker Hub image)
aws ecr create-repository \
    --repository-name ollama \
    --region us-east-1

# Note the repository URIs, e.g.:
# ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot
```

---

## Step 4: Build and Push Docker Images

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push PsychBot image
docker build -t psychbot:latest .
docker tag psychbot:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest

# For Ollama, you can either:
# Option A: Use the official Docker Hub image (easier)
# Option B: Pull, tag, and push to your ECR (for more control)
docker pull ollama/ollama:latest
docker tag ollama/ollama:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ollama:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ollama:latest
```

---

## Step 5: Deploy to AWS ECS (Recommended)

### 5.1: Create ECS Cluster

```bash
aws ecs create-cluster \
    --cluster-name psychbot-cluster \
    --region us-east-1
```

### 5.2: Create Task Execution Role

Create an IAM role that allows ECS to pull images and access secrets:

```bash
# Create trust policy
cat > ecs-task-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://ecs-task-trust-policy.json

# Attach AWS managed policy for ECS task execution
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create custom policy for Secrets Manager access
cat > secrets-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:psychbot/*"
      ]
    }
  ]
}
EOF

# Replace ACCOUNT_ID with your AWS account ID
# Then create and attach the policy
aws iam create-policy \
    --policy-name PsychBotSecretsAccess \
    --policy-document file://secrets-policy.json

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::ACCOUNT_ID:policy/PsychBotSecretsAccess
```

### 5.3: Create EFS File System (for persistent storage)

ChromaDB needs persistent storage across container restarts:

```bash
# Create EFS file system
aws efs create-file-system \
    --performance-mode generalPurpose \
    --throughput-mode bursting \
    --encrypted \
    --tags Key=Name,Value=psychbot-efs \
    --region us-east-1

# Note the FileSystemId returned, e.g., fs-12345678

# Create mount targets in your VPC subnets
# Replace with your actual subnet IDs and security group ID
aws efs create-mount-target \
    --file-system-id fs-12345678 \
    --subnet-id subnet-xxxxx \
    --security-groups sg-xxxxx
```

### 5.4: Create Task Definition

Create a file `task-definition.json`:

```json
{
  "family": "psychbot-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "8192",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ollama",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ollama:latest",
      "portMappings": [
        {
          "containerPort": 11434,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "entryPoint": ["/bin/sh", "-c"],
      "command": [
        "/bin/ollama serve & sleep 10 && ollama pull llama3:8b && wait"
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/psychbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ollama"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:11434 || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 5,
        "startPeriod": 90
      }
    },
    {
      "name": "psychbot",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest",
      "portMappings": [
        {
          "containerPort": 9000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "dependsOn": [
        {
          "containerName": "ollama",
          "condition": "HEALTHY"
        }
      ],
      "environment": [
        {
          "name": "OLLAMA_BASE_URL",
          "value": "http://localhost:11434"
        }
      ],
      "secrets": [
        {
          "name": "GOOGLE_CREDENTIALS_JSON",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:psychbot/google-credentials-XXXXX"
        },
        {
          "name": "SENDGRID_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:psychbot/sendgrid-api-key-XXXXX"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "chroma-data",
          "containerPath": "/app/docs",
          "readOnly": false
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/psychbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "psychbot"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:9000/docs || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 120
      }
    }
  ],
  "volumes": [
    {
      "name": "chroma-data",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "transitEncryption": "ENABLED"
      }
    }
  ]
}
```

Register the task definition:

```bash
# Create CloudWatch log group first
aws logs create-log-group \
    --log-group-name /ecs/psychbot \
    --region us-east-1

# Register task definition
aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --region us-east-1
```

### 5.5: Create ECS Service

```bash
aws ecs create-service \
    --cluster psychbot-cluster \
    --service-name psychbot-service \
    --task-definition psychbot-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
    --region us-east-1
```

### 5.6: Set Up Application Load Balancer (Optional)

For production, add an ALB:

```bash
# Create target group
aws elbv2 create-target-group \
    --name psychbot-targets \
    --protocol HTTP \
    --port 9000 \
    --vpc-id vpc-xxxxx \
    --target-type ip \
    --health-check-path /docs

# Create load balancer
aws elbv2 create-load-balancer \
    --name psychbot-alb \
    --subnets subnet-xxxxx subnet-yyyyy \
    --security-groups sg-xxxxx

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn <alb-arn> \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=<target-group-arn>

# Update ECS service to use the load balancer
aws ecs update-service \
    --cluster psychbot-cluster \
    --service psychbot-service \
    --load-balancers targetGroupArn=<target-group-arn>,containerName=psychbot,containerPort=9000
```

---

## Alternative: AWS App Runner (Simpler, but no Ollama support)

**Note:** App Runner doesn't support multi-container deployments easily. For a simpler setup, consider switching to AWS Bedrock or OpenAI instead of Ollama.

If you switch LLM providers, you can use App Runner:

```bash
aws apprunner create-service \
    --service-name psychbot \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest",
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": true
    }' \
    --instance-configuration '{
        "Cpu": "2 vCPU",
        "Memory": "4 GB"
    }'
```

---

## Step 6: Monitor and Debug

```bash
# Check service status
aws ecs describe-services \
    --cluster psychbot-cluster \
    --services psychbot-service

# View logs
aws logs tail /ecs/psychbot --follow

# List running tasks
aws ecs list-tasks \
    --cluster psychbot-cluster \
    --service-name psychbot-service
```

---

## Cost Estimates (us-east-1)

- **ECS Fargate (2 vCPU, 8GB RAM)**: ~$60-80/month for 24/7 operation
- **EFS Storage**: ~$0.30/GB/month (typically <1GB for ChromaDB)
- **ALB**: ~$16/month + data transfer
- **Secrets Manager**: $0.40/secret/month
- **ECR Storage**: $0.10/GB/month

**Total: ~$80-100/month** for a basic production setup

---

## Security Best Practices

1. **Never commit credentials** - Use Secrets Manager
2. **Enable encryption** - EFS and secrets are encrypted
3. **Use private subnets** - Route traffic through NAT Gateway
4. **Enable VPC Flow Logs** - Monitor network traffic
5. **Regular updates** - Keep base images updated
6. **IAM least privilege** - Only grant necessary permissions

---

## Troubleshooting

### Container fails to start
```bash
# Check CloudWatch logs
aws logs tail /ecs/psychbot --follow

# Common issues:
# - Secrets Manager permissions
# - Ollama model download timeout (increase startPeriod)
# - Memory limits too low
```

### Can't connect to Ollama
```bash
# Verify Ollama container is healthy
aws ecs describe-tasks \
    --cluster psychbot-cluster \
    --tasks <task-id>

# Check OLLAMA_BASE_URL is set to http://localhost:11434
# Make sure containers share the same network (awsvpc mode)
```

### Credentials not loading
```bash
# Test secret access
aws secretsmanager get-secret-value \
    --secret-id psychbot/google-credentials

# Verify task execution role has secretsmanager:GetSecretValue permission
# Check secret ARNs in task definition match actual secrets
```

---

## Updating the Application

```bash
# 1. Build new image
docker build -t psychbot:latest .

# 2. Tag and push
docker tag psychbot:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/psychbot:latest

# 3. Force new deployment (ECS will pull latest image)
aws ecs update-service \
    --cluster psychbot-cluster \
    --service psychbot-service \
    --force-new-deployment
```

---

## Next Steps

1. Set up custom domain with Route 53
2. Add HTTPS with ACM certificate
3. Implement CI/CD with GitHub Actions or CodePipeline
4. Add monitoring with CloudWatch alarms
5. Set up backup strategy for EFS

For questions or issues, refer to the main README.md or create an issue on GitHub.
