"""
Embeddings module for generating vector representations of documents
"""
import os
import logging
from typing import List
import openai

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings using OpenAI API"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.model
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
            except Exception as e:
                logger.error(f"Error processing text {i}: {e}")
                embeddings.append([])  # Empty embedding
        
        return embeddings
