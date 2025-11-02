# Step-by-Step Deployment Guide

## Quick Navigation

- **Local Development** (15 minutes) - Start here if you want to test locally
- **Production EKS Deployment** (45 minutes) - For cloud deployment on AWS

---

## Option 1: Local Development Deployment (15 minutes)

### Prerequisites
- Docker Desktop installed
- Node.js 18+ installed
- Python 3.11+ installed
- Git

### Step-by-Step Commands

#### 1. Start Qdrant Vector Database (Required)
```bash
# Start Qdrant in Docker
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# Verify it's running
curl http://localhost:6333
```

#### 2. Get API Keys

**NVIDIA API Key:**
- Visit https://build.nvidia.com/
- Sign in and get your API key
- Copy it (starts with `nvapi-`)

**Google API Key:**
- Visit https://aistudio.google.com/apikey
- Create new key
- Copy it

#### 3. Configure Environment Variables

```bash
cd nvdia-ag-ui/agent

# Create .env file
cat > .env << 'EOF'
GOOGLE_API_KEY=your-google-api-key-here
PORT=8000
EOF

# For image pipeline (optional if using product search)
cd ../../image_embeddings_pipeline

cat > .env << 'EOF'
NVIDIA_API_KEY=nvapi-XXXXX
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=image_embeddings
EMBEDDING_DIM=4096
EOF
```

#### 4. Install and Run Application

```bash
# Navigate to UI directory
cd ../nvdia-ag-ui

# Install dependencies (this also sets up Python agent)
npm install

# Start both UI and Agent backend
npm run dev

# Alternative: Run separately
# npm run dev:ui      # UI only on port 3000
# npm run dev:agent   # Agent only on port 8000
```

#### 5. Access the Application

Open your browser: **http://localhost:3000**

#### 6. Verify Everything Works

Test these prompts in the chat interface:
- "Show me sales data for the last month"
- "Analyze inventory levels"
- "What are the top selling products?"

---

## Option 2: Production AWS EKS Deployment (45 minutes)

### Prerequisites

#### Software Required
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Verify Installation
```bash
aws --version       # Should show v2.x
kubectl version --client
eksctl version
docker --version
```

### Step-by-Step EKS Deployment

#### Step 1: Configure AWS Credentials (2 minutes)

```bash
# Configure AWS CLI
aws configure

# You'll be prompted for:
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region name: us-east-1
# Default output format: json

# Verify credentials
aws sts get-caller-identity
```

#### Step 2: Create EKS Cluster (15-20 minutes)

```bash
cd k8s

# Make script executable
chmod +x create-eks-cluster.sh

# Create cluster
./create-eks-cluster.sh

# Wait for completion (15-20 minutes)
# This script will:
# - Create EKS cluster with 3 t3.xlarge nodes
# - Install AWS Load Balancer Controller
# - Install EBS CSI Driver
# - Configure OIDC provider
```

**Monitor progress:**
```bash
# In a new terminal, watch cluster creation
watch -n 10 kubectl get nodes
```

#### Step 3: Configure Secrets (2 minutes)

```bash
# Create namespace
kubectl create namespace nvidia-retail-ai

# Create API keys secret
# REPLACE with your actual keys!
kubectl create secret generic api-keys \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY \
  --from-literal=nvidia-api-key=nvapi-YOUR_NVIDIA_KEY \
  -n nvidia-retail-ai

# Verify secret created
kubectl get secrets -n nvidia-retail-ai
```

#### Step 4: Build and Deploy Application (10-15 minutes)

```bash
# Make deploy script executable
chmod +x deploy.sh

# Build and deploy
./deploy.sh

# This will:
# 1. Create ECR repositories
# 2. Build Docker images for UI and Agent
# 3. Push images to ECR
# 4. Deploy all Kubernetes resources
# 5. Wait for pods to be ready
```

**Monitor deployment:**
```bash
# Watch pods starting up
watch -n 5 kubectl get pods -n nvidia-retail-ai

# Expected output after 5-10 minutes:
# NAME                             READY   STATUS    RESTARTS   AGE
# agent-backend-xxx                1/1     Running   0          5m
# agent-backend-yyy                1/1     Running   0          5m
# qdrant-zzz                       1/1     Running   0          6m
# ui-frontend-aaa                  1/1     Running   0          5m
# ui-frontend-bbb                  1/1     Running   0          5m
```

#### Step 5: Get Application URL (2-3 minutes)

```bash
# Get ingress URL (may take 2-3 minutes to provision)
kubectl get ingress -n nvidia-retail-ai

# Wait for ADDRESS column to show a URL
# Example: xxxxx.us-east-1.elb.amazonaws.com

# Save URL to variable
export APP_URL=$(kubectl get ingress nvidia-retail-ai-ingress -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Display URL
echo "Your application is available at: http://${APP_URL}"
```

#### Step 6: Verify Deployment

```bash
# Check all resources
kubectl get all -n nvidia-retail-ai

# Check pod logs
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# Test application
curl http://${APP_URL}
```

Open browser: **http://YOUR-LOAD-BALANCER-URL**

---

## Common Commands

### Monitoring

```bash
# View all resources
kubectl get all -n nvidia-retail-ai

# Check pod status
kubectl get pods -n nvidia-retail-ai

# View logs (follow mode)
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# View recent events
kubectl get events -n nvidia-retail-ai --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n nvidia-retail-ai
kubectl top nodes
```

### Debugging

```bash
# Describe pod for troubleshooting
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Port forward to access services locally
kubectl port-forward svc/ui-frontend 3000:3000 -n nvidia-retail-ai
kubectl port-forward svc/qdrant 6333:6333 -n nvidia-retail-ai

# Exec into pod
kubectl exec -it <pod-name> -n nvidia-retail-ai -- /bin/bash

# Restart deployment
kubectl rollout restart deployment/agent-backend -n nvidia-retail-ai
kubectl rollout restart deployment/ui-frontend -n nvidia-retail-ai
```

### Scaling

```bash
# Scale up
kubectl scale deployment agent-backend --replicas=4 -n nvidia-retail-ai
kubectl scale deployment ui-frontend --replicas=3 -n nvidia-retail-ai

# Scale down
kubectl scale deployment agent-backend --replicas=1 -n nvidia-retail-ai

# Auto-scaling (optional)
kubectl autoscale deployment agent-backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n nvidia-retail-ai
```

### Updates

```bash
# Update image
kubectl set image deployment/agent-backend \
  agent-backend=<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/agent-backend:v2 \
  -n nvidia-retail-ai

# Update environment variable
kubectl set env deployment/agent-backend ENVIRONMENT=production -n nvidia-retail-ai

# Edit deployment directly
kubectl edit deployment agent-backend -n nvidia-retail-ai
```

---

## Troubleshooting

### Issue: Pods stuck in ImagePullBackOff

```bash
# Check ECR authentication
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Rebuild and push images
cd k8s
./deploy.sh
```

### Issue: Pods stuck in CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n nvidia-retail-ai

# Common causes:
# 1. Missing secrets - verify: kubectl get secrets -n nvidia-retail-ai
# 2. Cannot connect to Qdrant - check: kubectl get pods -n nvidia-retail-ai
# 3. Invalid API keys - recreate secrets
```

### Issue: Load balancer not provisioning

```bash
# Check ALB controller
kubectl get deployment -n kube-system aws-load-balancer-controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Verify ingress configuration
kubectl describe ingress nvidia-retail-ai-ingress -n nvidia-retail-ai
```

### Issue: Cannot access application

```bash
# Check if ingress has address
kubectl get ingress -n nvidia-retail-ai

# Check service endpoints
kubectl get endpoints -n nvidia-retail-ai

# Port forward to test directly
kubectl port-forward svc/ui-frontend 3000:3000 -n nvidia-retail-ai
# Then access: http://localhost:3000
```

---

## Cleanup

### Local Development

```bash
# Stop application (Ctrl+C in terminal)

# Stop Qdrant
docker stop qdrant
docker rm qdrant

# Clean volumes (optional - removes data)
docker volume rm qdrant_storage
```

### EKS Deployment

```bash
cd k8s
chmod +x cleanup.sh
./cleanup.sh

# This will prompt you to delete:
# 1. Namespace (yes)
# 2. ECR repositories (yes if you want to save costs)
# 3. EKS cluster (yes to fully clean up - saves $315/month)
# 4. IAM policies (yes)
```

**Manual cleanup:**
```bash
# Delete namespace only
kubectl delete namespace nvidia-retail-ai

# Delete EKS cluster
eksctl delete cluster --name nvidia-retail-ai-cluster --region us-east-1

# Delete ECR repositories
aws ecr delete-repository --repository-name nvidia-retail-frontend --region us-east-1 --force
aws ecr delete-repository --repository-name nvidia-retail-agent --region us-east-1 --force
```

---

## Cost Estimates

### Local Development
- **Free** (uses local resources)

### AWS EKS (24/7 operation)

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| EKS Control Plane | Standard | $73 |
| EC2 Nodes | 3x t3.xlarge | $220 |
| Load Balancer | 1 ALB | $20 |
| EBS Storage | 20GB | $2 |
| **TOTAL** | | **~$315** |

**Cost savings:**
- Stop cluster off-hours: ~50% savings
- Use Spot instances: ~70% savings
- Scale to 2 nodes: ~30% savings

---

## Next Steps After Deployment

### Security Hardening
1. Configure SSL/TLS certificate (ACM)
2. Set up custom domain
3. Enable Pod Security Standards
4. Configure Network Policies
5. Enable EKS audit logging

### Monitoring Setup
1. Install CloudWatch Container Insights
2. Set up custom metrics
3. Configure alarms
4. Set up budget alerts

### Production Readiness
1. Configure auto-scaling (HPA)
2. Set up CI/CD pipeline
3. Implement backup strategy for Qdrant
4. Load testing
5. Document runbooks

---

## Quick Reference

### Important URLs

- **Local UI**: http://localhost:3000
- **Local Agent API**: http://localhost:8000
- **Local Qdrant Dashboard**: http://localhost:6333/dashboard
- **NVIDIA NIM**: https://build.nvidia.com/
- **Google AI Studio**: https://aistudio.google.com/apikey
- **AWS Console**: https://console.aws.amazon.com/

### Important Files

- Environment config: `nvdia-ag-ui/agent/.env`
- Docker files: `nvdia-ag-ui/Dockerfile`, `nvdia-ag-ui/agent/Dockerfile`
- K8s manifests: `k8s/base/*.yaml`
- Deployment scripts: `k8s/*.sh`

### Support Resources

- Full docs: `k8s/README.md`
- Quick start: `k8s/QUICK_START.md`
- Architecture: `k8s/DEPLOYMENT_SUMMARY.md`
- Project guide: `CLAUDE.md`

---

## Summary

**For local testing:** Use Option 1 (15 minutes)
**For production:** Use Option 2 (45 minutes, ~$315/month)

**Questions?** Check the full documentation in `k8s/README.md`
