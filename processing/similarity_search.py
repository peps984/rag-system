# processing/similarity_search.py
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.models import DocumentChunk
from processing.embedding_generator import EmbeddingGenerator

class SimilaritySearch:
    """
    Search for chunks using cosine similarity
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_generator = EmbeddingGenerator()
    
    def search(self, query: str, top_k: int = 5, document_id: int = None) -> List[Dict]:
        # generate embeddings of the query
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # convert query_embedding to use it with pgvector 
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # build query SQL
        
        # "1 - (embedding <=> :query_embedding::vector)" convert distance
        # between vectors in similarity
        
        sql_query = """
            SELECT 
                id,
                document_id,
                chunk_index,
                content,
                char_count,
                1 - (embedding <=> :query_embedding ::vector) as similarity
            FROM document_chunks
            WHERE embedding IS NOT NULL
        """
        
        params = {"query_embedding": embedding_str}
        
        # optional filter for document id
        if document_id:
            sql_query += " AND document_id = :document_id"
            params["document_id"] = document_id
        
        # complete the query ordering by similary and limiting results
        sql_query += """
            ORDER BY similarity DESC
            LIMIT :top_k
        """
        params["top_k"] = top_k
        
        # execute the query
        result = self.db.execute(text(sql_query), params)
        
        # format results
        results = []
        for row in result:
            results.append({
                "chunk_id": row.id,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "char_count": row.char_count,
                "similarity": float(row.similarity)
            })
        
        return results