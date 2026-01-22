from openai import OpenAI
from typing import List
from config.settings import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

class EmbeddingGenerator:
    """
    Generate embeddings using OpenAI
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            return embedding
        
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings of multiple documents
        """
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
        
        except Exception as e:
            raise Exception(f"Error generating batch embeddings: {str(e)}")