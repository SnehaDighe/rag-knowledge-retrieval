"""
Data ingestion module for loading and processing documents
"""
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handle data ingestion from various sources"""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents = []

    def ingest_text_files(self) -> List[Dict]:
        """Ingest text files from directory"""
        logger.info(f"Ingesting text files from {self.data_path}")
        
        for filename in os.listdir(self.data_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.data_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append({
                        'filename': filename,
                        'content': content,
                        'type': 'text'
                    })
        
        logger.info(f"Ingested {len(self.documents)} documents")
        return self.documents

    def chunk_documents(self, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split documents into chunks"""
        chunks = []
        
        for doc in self.documents:
            content = doc['content']
            for i in range(0, len(content), chunk_size - overlap):
                chunk = content[i:i + chunk_size]
                chunks.append({
                    'source': doc['filename'],
                    'content': chunk,
                    'chunk_id': len(chunks)
                })
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
