import pinecone
from typing import List, Dict, Any
import logging
import openai
import tiktoken
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeManager:
    def __init__(self, api_key: str, environment: str, index_name: str, openai_api_key: str):
        pinecone.init(api_key=api_key, environment=environment)
        openai.api_key = openai_api_key
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=1536,
                metric='cosine'
            )
            
        self.index = pinecone.Index(index_name)

    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def _prepare_text(self, scholarship: Dict[str, Any]) -> str:
        # Create a structured text representation
        text_parts = [
            f"Title: {scholarship['title']}",
            f"Description: {scholarship['description']}",
            f"Eligibility: {', '.join(scholarship['eligibility'])}",
            f"Award: {scholarship['award']}",
            f"Deadline: {scholarship['deadline']}",
            f"Application Process: {', '.join(scholarship['application_process'])}",
            f"Documents Required: {', '.join(scholarship['documents_required'])}",
            f"Education Level: {scholarship['education_level']}",
            f"Country: {scholarship['country']}"
        ]
        return " | ".join(text_parts)

    def upsert_scholarships(self, scholarships: List[Dict]) -> None:
        try:
            vectors = []
            for i, scholarship in enumerate(scholarships):
                text = self._prepare_text(scholarship)
                embedding = self._get_embedding(text)
                
                vectors.append((
                    str(i),
                    embedding,
                    scholarship
                ))
            
            # Upsert in batches
            batch_size = 50  # Reduced batch size for better handling
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}")
                
            logger.info(f"Successfully upserted {len(scholarships)} scholarships")
            
        except Exception as e:
            logger.error(f"Error upserting scholarships: {e}")
            raise

    def query_scholarships(self, query: str, top_k: int = 5, filters: Dict = None) -> List[Dict]:
        try:
            query_embedding = self._get_embedding(query)
            
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filters:
                query_params["filter"] = filters
            
            results = self.index.query(**query_params)
            
            return [match.metadata for match in results.matches]
            
        except Exception as e:
            logger.error(f"Error querying scholarships: {e}")
            return [] 
