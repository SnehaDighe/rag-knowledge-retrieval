#!/bin/bash
# Clean up local Kubernetes deployment

NAMESPACE="rag-system"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🗑️  Cleaning up K8s deployment..."
echo ""

kubectl delete -k "$SCRIPT_DIR" --ignore-not-found=true

echo "✅ Cleanup complete!"
echo ""
echo "To remove the namespace entirely:"
echo "  kubectl delete namespace $NAMESPACE"
