# Quick Start for Local Testing

This guide helps you test the Kubernetes manifests locally using minikube or kind.

## Prerequisites

1. **Docker** - For building images
   ```bash
   docker --version
   ```

2. **Kubernetes Cluster** - One of:
   - **Minikube** (recommended for beginners)
     ```bash
     brew install minikube
     minikube start
     ```
   - **Kind** (Kubernetes in Docker)
     ```bash
     brew install kind
     kind create cluster
     ```

3. **kubectl** - Kubernetes command-line tool
   ```bash
   brew install kubectl
   kubectl cluster-info
   ```

4. **Kustomize** (optional, used by deploy script)
   ```bash
   brew install kustomize
   ```

## Deploy with Script (Recommended)

The easiest way to deploy locally:

```bash
# Make script executable
chmod +x k8s/deploy-local.sh

# Deploy to your local cluster
./k8s/deploy-local.sh

# Or build images first, then deploy
./k8s/deploy-local.sh --build
```

## Manual Deployment

If you prefer step-by-step control:

### 1. Build Docker Images

```bash
# Build Flask image
docker build -t rag-flask:latest -f Dockerfile .

# Build Node.js image
docker build -t rag-nodejs:latest -f backend-nodejs/Dockerfile ./backend-nodejs

# Verify images
docker images | grep rag
```

### 2. Load Images into Cluster

**For Minikube:**
```bash
minikube image load rag-flask:latest
minikube image load rag-nodejs:latest
```

**For Kind:**
```bash
kind load docker-image rag-flask:latest
kind load docker-image rag-nodejs:latest
```

### 3. Create and Update Secret File

Copy the example secret file and update with your credentials:

```bash
cp secret.yaml.example secret.yaml
vi secret.yaml
```

Update these fields:
```yaml
stringData:
  OPENAI_API_KEY: "sk-..."      # Your OpenAI key
  PINECONE_API_KEY: "your-key"   # Your Pinecone key
```

⚠️ **The `secret.yaml` file is in `.gitignore` - it will not be committed to git.**

### 4. Deploy Manifests

```bash
# Deploy all at once using Kustomize
kubectl apply -k k8s/

# Or deploy individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml          # Use the secret.yaml file you created from .example
kubectl apply -f k8s/python-deployment.yaml
kubectl apply -f k8s/nodejs-deployment.yaml
kubectl apply -f k8s/python-service.yaml
kubectl apply -f k8s/nodejs-service.yaml
```

### 5. Monitor Deployment

```bash
# Watch pods starting
kubectl get pods -n rag-system -w

# Check specific pod
kubectl describe pod -n rag-system <pod-name>

# View logs
kubectl logs -n rag-system -l app=flask-api
kubectl logs -n rag-system -l app=nodejs-api
```

## Access Services Locally

### Port Forwarding

```bash
# In one terminal - Forward Flask
kubectl port-forward -n rag-system svc/flask-api 5000:5000

# In another terminal - Forward Node.js
kubectl port-forward -n rag-system svc/nodejs-api 3000:3000
```

### Test Endpoints

```bash
# Test Flask API
curl http://localhost:5000/health

# Test Node.js API
curl http://localhost:3000/health
```

### Get Service IPs (Cluster-internal)

```bash
kubectl get svc -n rag-system

# Shows internal cluster IPs for pod-to-pod communication
```

## Scaling & Testing

### Scale Deployments

```bash
# Increase Flask replicas
kubectl scale deployment -n rag-system flask-api --replicas=3

# Increase Node.js replicas
kubectl scale deployment -n rag-system nodejs-api --replicas=3

# Scale down
kubectl scale deployment -n rag-system flask-api --replicas=1
```

### Update Image

```bash
# After building a new image
docker build -t rag-flask:latest -f Dockerfile .

# For minikube
minikube image load rag-flask:latest

# For kind
kind load docker-image rag-flask:latest

# Force pods to redeploy
kubectl rollout restart deployment -n rag-system flask-api
```

### Test Resource Limits

Monitor how pods behave under load:

```bash
# Watch resource usage
kubectl top pods -n rag-system

# Or for specific pod
kubectl top pod -n rag-system <pod-name>
```

## Cleanup

### Remove Everything

```bash
# Using script
./k8s/cleanup.sh

# Or manually
kubectl delete -k k8s/
```

### Remove Namespace (including all resources)

```bash
kubectl delete namespace rag-system
```

### Keep Cluster Running for Next Time

```bash
# Minikube - just delete pods/deployments
kubectl delete deployment -n rag-system --all

# Or stop the whole cluster
minikube stop  # Resume with: minikube start
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod -n rag-system <pod-name>

# Check recent errors
kubectl get events -n rag-system --sort-by='.lastTimestamp'
```

### Image Pull Errors

```bash
# List available images in cluster
minikube image ls  # For minikube
docker images      # On host machine

# Rebuild and reload
docker build -t rag-flask:latest -f Dockerfile .
minikube image load rag-flask:latest
```

### CrashLoopBackOff

Usually means app failed to start:

```bash
# Check logs
kubectl logs -n rag-system -l app=flask-api --previous

# Verify your backend code is working
python backend-python/app.py
npm start  # from backend-nodejs/
```

### Port Forward Not Working

```bash
# Check if service exists
kubectl get svc -n rag-system

# Check if pods are running
kubectl get pods -n rag-system

# Try direct pod port-forward
kubectl port-forward -n rag-system pod/<pod-name> 5000:5000
```

## Next Steps

Once testing locally is successful:

1. **Push to your container registry** (Docker Hub, ECR, etc.)
2. **Update deployment image references** to use registry URLs
3. **Use sealed-secrets or external-secrets** for production credentials
4. **Deploy to real Kubernetes cluster**

See [README.md](README.md) for production deployment steps.
