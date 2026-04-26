# ⚠️ Kubernetes Manifests - Important Notes

## Before Using These Files

### 1. Create Secret File from Template
First, create your secret file from the example template:

```bash
cp secret.yaml.example secret.yaml
```

**NEVER commit `secret.yaml` to git!** It's already in `.gitignore` to prevent accidental commits.

Update it with your actual API keys:
```bash
vi secret.yaml
```

Update these fields:
```yaml
stringData:
  OPENAI_API_KEY: "sk-..."      # Your OpenAI key
  PINECONE_API_KEY: "your-key"   # Your Pinecone key
```

### 2. For Development with Multiple Environments
You can create environment-specific copies:

```bash
cp secret.yaml.example secret.yaml.dev
# cp secret.yaml.example secret.yaml.staging
```

Then deploy using:
```bash
kubectl apply -f secret.yaml.dev
```

All variations of secret.yaml are ignored by git (.gitignore prevents accidental commits).

### 3. For Production
Use one of these secure solutions instead:
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- AWS Secrets Manager / Azure Key Vault
- HashiCorp Vault

### 4. Update Docker Image References
If using a container registry (Docker Hub, ECR, GCR, etc.), update:

**In `python-deployment.yaml`:**
```yaml
image: yourusername/rag-flask:latest  # Change this
```

**In `nodejs-deployment.yaml`:**
```yaml
image: yourusername/rag-nodejs:latest  # Change this
```

### 5. Update Ingress Hostname
In `ingress.yaml`, change:
```yaml
- host: rag.example.com  # Change to your domain
```

### 6. Ensure Health Check Endpoints
The deployments expect these endpoints:
- **Flask API**: `/health` and `/ready` on port 5000
- **Node.js API**: `/health` and `/ready` on port 3000

Add these to your application if they don't exist:

**Python (Flask):**
```python
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.route('/ready')
def ready():
    # Check if your service dependencies are ready
    return {'ready': True}, 200
```

**Node.js (Express):**
```javascript
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.get('/ready', (req, res) => {
  // Check if your service dependencies are ready
  res.json({ ready: true });
});
```

## Quick Start

### For Local Development Testing:
```bash
chmod +x k8s/deploy-local.sh
./k8s/deploy-local.sh --build
```
See [LOCAL-TESTING.md](LOCAL-TESTING.md) for detailed instructions.

### For Production Deployment:
See [README.md](README.md) for comprehensive setup and deployment instructions.

## File Structure

```
k8s/
├── README.md                    # Production deployment guide
├── LOCAL-TESTING.md             # Local K8s testing guide
├── IMPORTANT.md                 # This file
├── namespace.yaml               # Kubernetes namespace
├── configmap.yaml               # Configuration values
├── secret.yaml                  # ⚠️ API keys (update before use)
├── python-deployment.yaml       # Flask deployment
├── nodejs-deployment.yaml       # Node.js deployment
├── python-service.yaml          # Flask service
├── nodejs-service.yaml          # Node.js service
├── ingress.yaml                 # Ingress configuration
├── hpa.yaml                     # Auto-scaling (optional)
├── persistent-volume.yaml       # Storage (optional)
├── kustomization.yaml           # Kustomize configuration
├── deploy-local.sh              # Deployment script (executable)
└── cleanup.sh                   # Cleanup script (executable)
```

## Deployment Checklist

- [ ] Kubernetes cluster is running (minikube/kind/cloud)
- [ ] `kubectl` is configured and working
- [ ] Docker images are built
- [ ] Images are pushed to registry OR loaded into local cluster
- [ ] `secret.yaml` updated with real API keys (or `secret.yaml.local` created)
- [ ] Image references updated in deployment files (if using registry)
- [ ] Ingress hostname updated (if using ingress)
- [ ] Health check endpoints implemented in your app
- [ ] `deploy-local.sh` is executable: `chmod +x k8s/deploy-local.sh`

## Common Commands

```bash
# Deploy
kubectl apply -k k8s/

# Check status
kubectl get all -n rag-system
kubectl get pods -n rag-system -w

# View logs
kubectl logs -n rag-system -l app=flask-api -f

# Port forward
kubectl port-forward -n rag-system svc/flask-api 5000:5000

# Remove deployment
kubectl delete -k k8s/
# Or
./k8s/cleanup.sh
```

## Questions?

See the README.md and LOCAL-TESTING.md files for detailed instructions and troubleshooting.
