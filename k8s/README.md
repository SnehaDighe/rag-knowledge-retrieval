# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the RAG Knowledge Retrieval System to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (v1.20+)
- `kubectl` configured to access your cluster
- Docker images built and available (see instructions below)
- API keys for OpenAI and Pinecone (will be configured as secrets)

## File Structure

- `namespace.yaml` - Kubernetes namespace for the application
- `configmap.yaml` - Configuration settings
- `secret.yaml` - Sensitive data (API keys) - **Update before deployment**
- `python-deployment.yaml` - Flask API deployment
- `nodejs-deployment.yaml` - Node.js API deployment
- `python-service.yaml` - Flask API service
- `nodejs-service.yaml` - Node.js API service
- `ingress.yaml` - Ingress configuration for external access
- `kustomization.yaml` - Kustomize configuration for managing all resources

## Setup Instructions

### 1. Build Docker Images

Build the images and push them to your container registry:

```bash
# Build Flask image
docker build -t rag-flask:latest .

# Build Node.js image
docker build -t rag-nodejs:latest ./backend-nodejs

# Push to registry (example with DockerHub)
docker tag rag-flask:latest yourusername/rag-flask:latest
docker tag rag-nodejs:latest yourusername/rag-nodejs:latest
docker push yourusername/rag-flask:latest
docker push yourusername/rag-nodejs:latest
```

Update the image references in `python-deployment.yaml` and `nodejs-deployment.yaml` to match your registry.

### 2. Configure Secrets

Edit `secret.yaml` and replace the placeholder API keys with your actual keys:

```bash
# Update with your real API keys
vi k8s/secret.yaml
```

For production, consider using:
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- Cloud provider secret management (AWS Secrets Manager, Azure Key Vault, etc.)

### 3. Deploy Using Kustomize

```bash
# Deploy all resources at once
kubectl apply -k k8s/

# Verify deployment
kubectl get all -n rag-system
kubectl get pods -n rag-system
```

### 4. Deploy Individual Components (Optional)

If you prefer to deploy components individually:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create config and secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy services
kubectl apply -f k8s/python-deployment.yaml
kubectl apply -f k8s/nodejs-deployment.yaml
kubectl apply -f k8s/python-service.yaml
kubectl apply -f k8s/nodejs-service.yaml

# Set up ingress
kubectl apply -f k8s/ingress.yaml
```

## Verification

### Check Deployment Status

```bash
# Watch pods starting up
kubectl get pods -n rag-system -w

# Check logs
kubectl logs -n rag-system -l app=flask-api
kubectl logs -n rag-system -l app=nodejs-api

# Describe deployments
kubectl describe deployment -n rag-system
```

### Port Forwarding (for testing)

```bash
# Access Flask API
kubectl port-forward -n rag-system svc/flask-api 5000:5000

# Access Node.js API in another terminal
kubectl port-forward -n rag-system svc/nodejs-api 3000:3000
```

### Test Endpoints

```bash
# Flask health check
curl http://localhost:5000/health

# Node.js health check
curl http://localhost:3000/health
```

## Configuration

### Scaling Replicas

Modify the `replicas` field in deployment YAML files:

```yaml
spec:
  replicas: 3  # Change this value
```

Or use kubectl:

```bash
kubectl scale deployment -n rag-system flask-api --replicas=3
```

### Resource Limits

Adjust CPU and memory limits in the deployment files to match your cluster capacity:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Health Checks

The deployments include:
- **Liveness Probe**: Restarts unhealthy pods
- **Readiness Probe**: Removes pods from service during degradation

Ensure your applications expose `/health` and `/ready` endpoints.

## Ingress Setup

The `ingress.yaml` provides external access. Update:
- `host: rag.example.com` - Your domain name
- Ingress controller - Ensure NGINX or equivalent is installed

```bash
# Install NGINX Ingress Controller (if not present)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

## Cleanup

To remove all deployed resources:

```bash
# Using Kustomize
kubectl delete -k k8s/

# Or manually
kubectl delete namespace rag-system
```

## Advanced Features

### Persistent Storage

To add persistent volume claims for data:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-data-pvc
  namespace: rag-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Horizontal Pod Autoscaling

Enable auto-scaling based on CPU/memory usage:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flask-api-hpa
  namespace: rag-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Network Policies

Restrict traffic between pods for enhanced security:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rag-network-policy
  namespace: rag-system
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## Troubleshooting

### Pods Stuck in Pending

```bash
kubectl describe pod -n rag-system <pod-name>
kubectl get events -n rag-system --sort-by='.lastTimestamp'
```

### Image Pull Errors

Ensure images are available and correctly tagged:

```bash
kubectl get events -n rag-system | grep -i pull
```

### Startup Probe Failures

Check application logs and health endpoints:

```bash
kubectl logs -n rag-system -l app=flask-api --tail=50
```

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)
