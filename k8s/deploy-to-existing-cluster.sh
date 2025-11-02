#!/bin/bash

# Deploy to Existing EKS Cluster
# This script deploys the NVIDIA Retail AI application to an existing EKS cluster

set -e

CLUSTER_NAME="nvidia-retail-ai-cluster"
REGION="us-east-1"
NAMESPACE="nvidia-retail-ai"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "========================================="
echo "NVIDIA Retail AI - Deploy to Existing Cluster"
echo "========================================="
echo ""

# Step 1: Verify cluster exists and is active
echo "Step 1: Verifying cluster status..."
CLUSTER_STATUS=$(aws eks describe-cluster --name $CLUSTER_NAME --region $REGION --query 'cluster.status' --output text 2>/dev/null || echo "NOT_FOUND")

if [ "$CLUSTER_STATUS" != "ACTIVE" ]; then
    echo "❌ Error: Cluster '$CLUSTER_NAME' is not ACTIVE (status: $CLUSTER_STATUS)"
    echo "Please check your cluster status with:"
    echo "  aws eks describe-cluster --name $CLUSTER_NAME --region $REGION"
    exit 1
fi

echo "✅ Cluster is ACTIVE"
echo ""

# Step 2: Configure kubectl
echo "Step 2: Configuring kubectl..."
aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION
echo "✅ kubectl configured"
echo ""

# Step 3: Verify nodes are ready
echo "Step 3: Verifying nodes..."
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
if [ "$NODE_COUNT" -eq 0 ]; then
    echo "❌ Error: No nodes found in the cluster"
    exit 1
fi

echo "✅ Found $NODE_COUNT nodes"
kubectl get nodes
echo ""

# Step 4: Create namespace
echo "Step 4: Creating namespace..."
kubectl create namespace $NAMESPACE 2>/dev/null && echo "✅ Namespace created" || echo "ℹ️  Namespace already exists"
echo ""

# Step 5: Create secrets
echo "Step 5: Setting up API keys..."
echo ""
echo "⚠️  IMPORTANT: You need to provide your API keys"
echo ""
read -p "Enter your Google API key: " GOOGLE_API_KEY
read -p "Enter your NVIDIA API key: " NVIDIA_API_KEY

if [ -z "$GOOGLE_API_KEY" ] || [ -z "$NVIDIA_API_KEY" ]; then
    echo "❌ Error: Both API keys are required"
    exit 1
fi

# Delete existing secret if it exists
kubectl delete secret api-keys -n $NAMESPACE 2>/dev/null || true

# Create new secret
kubectl create secret generic api-keys \
  --from-literal=google-api-key=$GOOGLE_API_KEY \
  --from-literal=nvidia-api-key=$NVIDIA_API_KEY \
  -n $NAMESPACE

echo "✅ Secrets created"
echo ""

# Step 6: Create ECR repositories
echo "Step 6: Creating ECR repositories..."
aws ecr describe-repositories --repository-names nvidia-retail-frontend --region $REGION >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name nvidia-retail-frontend --region $REGION >/dev/null

aws ecr describe-repositories --repository-names nvidia-retail-agent --region $REGION >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name nvidia-retail-agent --region $REGION >/dev/null

echo "✅ ECR repositories ready"
echo ""

# Step 7: Build and push Docker images
echo "Step 7: Building Docker images..."
echo "This may take 5-10 minutes..."
echo ""

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push UI frontend
echo "Building UI frontend..."
cd ..
docker build -t nvidia-retail-frontend:latest -f nvdia-ag-ui/Dockerfile nvdia-ag-ui/
docker tag nvidia-retail-frontend:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-frontend:latest
echo "✅ UI frontend image pushed"
echo ""

# Build and push agent backend
echo "Building agent backend..."
docker build -t nvidia-retail-agent:latest -f nvdia-ag-ui/agent/Dockerfile nvdia-ag-ui/agent/
docker tag nvidia-retail-agent:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-agent:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/nvidia-retail-agent:latest
echo "✅ Agent backend image pushed"
echo ""

cd k8s

# Step 8: Update image references in manifests
echo "Step 8: Updating Kubernetes manifests..."
sed -i.bak "s|<ACCOUNT_ID>|$ACCOUNT_ID|g" base/ui-deployment.yaml
sed -i.bak "s|<ACCOUNT_ID>|$ACCOUNT_ID|g" base/agent-deployment.yaml
echo "✅ Manifests updated"
echo ""

# Step 9: Deploy Kubernetes resources
echo "Step 9: Deploying to Kubernetes..."
echo ""

# Deploy in order
echo "Deploying namespace..."
kubectl apply -f base/namespace.yaml

echo "Deploying ConfigMap..."
kubectl apply -f base/configmap.yaml

echo "Deploying Qdrant..."
kubectl apply -f base/qdrant-deployment.yaml

echo "Waiting for Qdrant to be ready (30 seconds)..."
sleep 30
kubectl wait --for=condition=ready pod -l app=qdrant -n $NAMESPACE --timeout=120s

echo "Deploying Agent backend..."
kubectl apply -f base/agent-deployment.yaml

echo "Waiting for Agent backend to be ready (30 seconds)..."
sleep 30
kubectl wait --for=condition=ready pod -l app=agent-backend -n $NAMESPACE --timeout=120s

echo "Deploying UI frontend..."
kubectl apply -f base/ui-deployment.yaml

echo "✅ All resources deployed"
echo ""

# Step 10: Wait for pods to be ready
echo "Step 10: Waiting for all pods to be ready..."
echo "This may take 3-5 minutes..."
kubectl wait --for=condition=ready pod --all -n $NAMESPACE --timeout=300s

echo ""
echo "✅ All pods are ready!"
echo ""

# Step 11: Get application URL
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
kubectl get pods -n $NAMESPACE
echo ""

echo "Getting application URL..."
echo "Note: Load balancer provisioning may take 2-3 minutes"
echo ""

# Wait for ingress to get an address
for i in {1..60}; do
    INGRESS_URL=$(kubectl get ingress nvidia-retail-ai-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    if [ -n "$INGRESS_URL" ]; then
        break
    fi
    echo "Waiting for load balancer... ($i/60)"
    sleep 5
done

if [ -n "$INGRESS_URL" ]; then
    echo ""
    echo "========================================="
    echo "✅ SUCCESS! Application is deployed!"
    echo "========================================="
    echo ""
    echo "🌐 Application URL: http://$INGRESS_URL"
    echo ""
    echo "Note: It may take 2-3 more minutes for the load balancer to be fully operational"
    echo ""
else
    echo ""
    echo "⚠️  Load balancer URL not available yet"
    echo "Run this command in a few minutes:"
    echo "  kubectl get ingress -n $NAMESPACE"
    echo ""
fi

echo "Useful commands:"
echo "  View pods:     kubectl get pods -n $NAMESPACE"
echo "  View logs:     kubectl logs -f deployment/agent-backend -n $NAMESPACE"
echo "  View ingress:  kubectl get ingress -n $NAMESPACE"
echo ""

# Restore original manifest files
mv base/ui-deployment.yaml.bak base/ui-deployment.yaml 2>/dev/null || true
mv base/agent-deployment.yaml.bak base/agent-deployment.yaml 2>/dev/null || true

echo "Deployment script completed!"
