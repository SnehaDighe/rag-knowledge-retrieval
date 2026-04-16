"""
Main entry point for RAG Knowledge Retrieval System
"""
import os
import logging
from dotenv import load_dotenv
from data_ingestion import DataIngestion
from embeddings import EmbeddingsGenerator
from semantic_search import SemanticSearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class KnowledgeRetrievalSystem:
    """Main RAG system"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.data_path = os.getenv('DATA_PATH', './data/documents')
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
        self.overlap = int(os.getenv('OVERLAP', 200))
        
        self.ingestion = DataIngestion(self.data_path)
        self.embeddings_gen = EmbeddingsGenerator(self.api_key)
        self.search_engine = None

    def initialize(self):
        """Initialize the system"""
        logger.info("Initializing Knowledge Retrieval System...")
        
        # Ingest documents
        documents = self.ingestion.ingest_text_files()
        chunks = self.ingestion.chunk_documents(self.chunk_size, self.overlap)
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embeddings_gen.generate_embeddings_batch(chunk_texts)
        
        # Initialize search engine
        self.search_engine = SemanticSearch(embeddings, chunks)
        logger.info("System initialized successfully")

    def query(self, query_text: str, k: int = 5) -> List[Dict]:
        """Query the knowledge base"""
        logger.info(f"Processing query: {query_text}")
        
        # Generate query embedding
        query_embedding = self.embeddings_gen.generate_embedding(query_text)
        
        # Search
        results = self.search_engine.search(query_embedding, k)
        
        return results


if __name__ == "__main__":
    system = KnowledgeRetrievalSystem()
    system.initialize()
    
    # Example query
    results = system.query("What is machine learning?")
    for result in results:
        print(f"Score: {result['score']:.2f}")
        print(f"Content: {result['document']['content'][:100]}...")
        print()
