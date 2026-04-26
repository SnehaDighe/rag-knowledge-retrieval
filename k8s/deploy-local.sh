#!/bin/bash
# Local Kubernetes deployment script for development/testing
# Requires: minikube or kind installed and running

set -e

NAMESPACE="rag-system"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 RAG Knowledge Retrieval - Local K8s Deployment"
echo "=================================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    echo "Install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if cluster is running
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ No Kubernetes cluster is running"
    echo "Start a local cluster: minikube start OR kind create cluster"
    exit 1
fi

echo "✅ Kubernetes cluster is ready"
echo ""

# Show cluster info
echo "📊 Cluster Info:"
kubectl cluster-info | head -2
echo ""

# Build and load Docker images (for local development)
if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "🔨 Building Docker images..."
    echo ""
    
    # Build Flask image
    echo "Building Flask image..."
    docker build -t rag-flask:latest -f Dockerfile .
    
    # Build Node.js image
    echo "Building Node.js image..."
    docker build -t rag-nodejs:latest -f backend-nodejs/Dockerfile ./backend-nodejs
    
    # Load images into local cluster (for minikube/kind)
    if command -v minikube &> /dev/null && minikube status &> /dev/null; then
        echo ""
        echo "📦 Loading images into minikube..."
        minikube image load rag-flask:latest
        minikube image load rag-nodejs:latest
        echo "✅ Images loaded into minikube"
    fi
    
    if command -v kind &> /dev/null; then
        echo ""
        echo "📦 Loading images into kind cluster..."
        kind load docker-image rag-flask:latest
        kind load docker-image rag-nodejs:latest
        echo "✅ Images loaded into kind cluster"
    fi
    
    echo ""
fi

# Deploy using Kustomize
echo "📝 Deploying K8s manifests..."
kubectl apply -k "$SCRIPT_DIR"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Checking deployment status..."
sleep 2

kubectl get all -n "$NAMESPACE"

echo ""
echo "🔍 Waiting for pods to be ready (this may take a minute)..."
kubectl wait --for=condition=ready pod -l app=flask-api -n "$NAMESPACE" --timeout=300s 2>/dev/null || true
kubectl wait --for=condition=ready pod -l app=nodejs-api -n "$NAMESPACE" --timeout=300s 2>/dev/null || true

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Port forward to access services:"
echo "   kubectl port-forward -n $NAMESPACE svc/flask-api 5000:5000"
echo "   kubectl port-forward -n $NAMESPACE svc/nodejs-api 3000:3000"
echo ""
echo "2. Check logs:"
echo "   kubectl logs -n $NAMESPACE -l app=flask-api -f"
echo "   kubectl logs -n $NAMESPACE -l app=nodejs-api -f"
echo ""
echo "3. Cleanup (remove deployment):"
echo "   kubectl delete -k $SCRIPT_DIR"
echo ""
