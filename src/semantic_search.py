"""
Semantic search module using FAISS and vector databases
"""
import logging
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Perform semantic search on embeddings"""

    def __init__(self, embeddings: List[List[float]], documents: List[Dict]):
        self.embeddings = np.array(embeddings)
        self.documents = documents
        self.dimension = len(embeddings[0]) if embeddings else 0
        
        try:
            import faiss
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(self.embeddings)
            logger.info("FAISS index created successfully")
        except ImportError:
            logger.warning("FAISS not available, using numpy for search")
            self.index = None

    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Search for top-k similar documents"""
        query_embedding = np.array([query_embedding])
        
        if self.index:
            distances, indices = self.index.search(query_embedding, k)
            results = []
            
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    results.append({
                        'document': self.documents[idx],
                        'distance': float(distances[0][i]),
                        'score': 1 / (1 + distances[0][i])
                    })
            
            return results
        else:
            # Fallback to numpy cosine similarity
            similarities = self._cosine_similarity(query_embedding[0], self.embeddings)
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            return [
                {
                    'document': self.documents[idx],
                    'score': float(similarities[idx])
                }
                for idx in top_indices
            ]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity"""
        return np.dot(b, a) / (np.linalg.norm(b, axis=1) * np.linalg.norm(a) + 1e-8)
