# Continue Deployment to Existing EKS Cluster

Your EKS cluster already exists! Follow these steps to deploy the application.

## Quick Option: Run Automated Script

```bash
cd k8s
chmod +x deploy-to-existing-cluster.sh
./deploy-to-existing-cluster.sh
```

This script will:
1. ✅ Verify cluster is active
2. ✅ Configure kubectl
3. ✅ Create namespace and secrets (will prompt for API keys)
4. ✅ Build and push Docker images
5. ✅ Deploy all Kubernetes resources
6. ✅ Provide application URL

**Time:** ~10-15 minutes

---

## Manual Option: Step-by-Step Commands

If you prefer to run commands manually:

### Step 1: Configure kubectl (30 seconds)

```bash
# Connect kubectl to your existing cluster
aws eks update-kubeconfig \
  --name nvidia-retail-ai-cluster \
  --region us-east-1

# Verify connection
kubectl get nodes
```

**Expected output:** Should show 3 nodes in Ready state

### Step 2: Create Namespace (10 seconds)

```bash
kubectl create namespace nvidia-retail-ai
```

### Step 3: Create Secrets (30 seconds)

**Get your API keys first:**
- Google API: https://aistudio.google.com/apikey
- NVIDIA API: https://build.nvidia.com/

```bash
# Replace YOUR_GOOGLE_KEY and YOUR_NVIDIA_KEY with actual keys
kubectl create secret generic api-keys \
  --from-literal=google-api-key=YOUR_GOOGLE_KEY \
  --from-literal=nvidia-api-key=YOUR_NVIDIA_KEY \
  -n nvidia-retail-ai

# Verify secret created
kubectl get secrets -n nvidia-retail-ai
```

### Step 4: Create ECR Repositories (1 minute)

```bash
# Get your AWS account ID
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export REGION=us-east-1

# Create ECR repositories
aws ecr create-repository --repository-name nvidia-retail-frontend --region $REGION
aws ecr create-repository --repository-name nvidia-retail-agent --region $REGION
```

### Step 5: Build and Push Docker Images (5-10 minutes)

```bash
# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Navigate to project root
cd /path/to/NVDIA-Retail-AI-Teams

# Build UI frontend
docker build -t nvidia-retail-frontend:latest \
  -f nvdia-ag-ui/Dockerfile \
  nvdia-ag-ui/

# Tag and push UI frontend
docker tag nvidia-retail-frontend:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-frontend:latest

# Build agent backend
docker build -t nvidia-retail-agent:latest \
  -f nvdia-ag-ui/agent/Dockerfile \
  nvdia-ag-ui/agent/

# Tag and push agent backend
docker tag nvidia-retail-agent:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-agent:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-agent:latest
```

### Step 6: Update Kubernetes Manifests (30 seconds)

```bash
cd k8s

# Update image references with your account ID
sed -i "s|<ACCOUNT_ID>|$ACCOUNT_ID|g" base/ui-deployment.yaml
sed -i "s|<ACCOUNT_ID>|$ACCOUNT_ID|g" base/agent-deployment.yaml
```

### Step 7: Deploy Kubernetes Resources (3-5 minutes)

```bash
# Deploy in order
kubectl apply -f base/namespace.yaml
kubectl apply -f base/configmap.yaml
kubectl apply -f base/qdrant-deployment.yaml

# Wait for Qdrant to be ready
kubectl wait --for=condition=ready pod -l app=qdrant -n nvidia-retail-ai --timeout=120s

# Deploy agent backend
kubectl apply -f base/agent-deployment.yaml

# Wait for agent to be ready
kubectl wait --for=condition=ready pod -l app=agent-backend -n nvidia-retail-ai --timeout=120s

# Deploy UI frontend
kubectl apply -f base/ui-deployment.yaml

# Wait for all pods
kubectl wait --for=condition=ready pod --all -n nvidia-retail-ai --timeout=300s
```

### Step 8: Verify Deployment (1 minute)

```bash
# Check all pods are running
kubectl get pods -n nvidia-retail-ai

# Expected output:
# NAME                             READY   STATUS    RESTARTS   AGE
# agent-backend-xxx                1/1     Running   0          2m
# agent-backend-yyy                1/1     Running   0          2m
# qdrant-zzz                       1/1     Running   0          3m
# ui-frontend-aaa                  1/1     Running   0          1m
# ui-frontend-bbb                  1/1     Running   0          1m
```

### Step 9: Get Application URL (2-3 minutes)

```bash
# Get ingress details
kubectl get ingress -n nvidia-retail-ai

# Wait for ADDRESS to appear (may take 2-3 minutes)
# Then get the URL
export APP_URL=$(kubectl get ingress nvidia-retail-ai-ingress \
  -n nvidia-retail-ai \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo "Application URL: http://$APP_URL"
```

---

## Troubleshooting

### Issue: Nodes not ready

```bash
# Check node status
kubectl get nodes

# Describe node for details
kubectl describe node <node-name>
```

### Issue: Pods stuck in ImagePullBackOff

```bash
# Check pod details
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Common fix: Re-authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Issue: Pods in CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n nvidia-retail-ai

# Common causes:
# 1. Missing or invalid secrets
# 2. Cannot connect to Qdrant (wait for it to be ready)
# 3. Missing environment variables
```

### Issue: Ingress not getting URL

```bash
# Check ingress controller
kubectl get pods -n kube-system | grep aws-load-balancer-controller

# Check ingress events
kubectl describe ingress nvidia-retail-ai-ingress -n nvidia-retail-ai

# If ALB controller is missing, install it:
cd k8s
./install-alb-controller.sh  # This is part of create-eks-cluster.sh
```

---

## Monitoring Commands

```bash
# Watch pods
watch kubectl get pods -n nvidia-retail-ai

# Stream logs
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# Check resource usage
kubectl top pods -n nvidia-retail-ai
kubectl top nodes

# View all resources
kubectl get all -n nvidia-retail-ai
```

---

## After Deployment

Once you get the application URL:

1. **Open in browser**: http://YOUR-LOAD-BALANCER-URL
2. **Test the application**:
   - Try asking: "Show me sales data"
   - Try asking: "Analyze inventory levels"
   - Try asking: "Search for red dress"

3. **Monitor the deployment**:
   ```bash
   kubectl get pods -n nvidia-retail-ai -w
   ```

---

## Quick Commands Reference

```bash
# Get application URL
kubectl get ingress -n nvidia-retail-ai

# Restart a deployment
kubectl rollout restart deployment/agent-backend -n nvidia-retail-ai

# Scale deployment
kubectl scale deployment agent-backend --replicas=4 -n nvidia-retail-ai

# Port forward for local access
kubectl port-forward svc/ui-frontend 3000:3000 -n nvidia-retail-ai

# Delete everything (cleanup)
kubectl delete namespace nvidia-retail-ai
```

---

## Summary

**Fastest path to deployment:**

```bash
cd k8s
chmod +x deploy-to-existing-cluster.sh
./deploy-to-existing-cluster.sh
```

This will handle everything automatically and provide you with the application URL at the end.

**Estimated time:** 10-15 minutes

---

**Questions?** Check the logs:
```bash
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
```
