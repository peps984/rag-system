from typing import List, Dict
from sqlalchemy.orm import Session
from openai import OpenAI
from processing.similarity_search import SimilaritySearch
from config.settings import OPENAI_API_KEY

class RAGService:
    """
    Retrieval-Augmented Generation service
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.searcher = SimilaritySearch(db)
    
    def build_context(self, chunks: List[Dict]) -> str:
        """
        Build the context from the chunks
        
        args: 
            chunks from similarity search
            
        returns:
            formatted context
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[document {chunk['document_id']}, section {chunk['chunk_index']}]\n"
                f"{chunk['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    def build_prompt(self, query: str, context: str) -> List[Dict[str, str]]:
        """
        Build the prompt
        """
        system_message = """You are an assistant for question-answering tasks. Provide accurate responses based STRICTLY on the provided search results.

Instructions:
1. ONLY answer using information explicitly found in the context
2. If the context doesn't contain enough information to fully answer the question, respond: "I don't have enough information to answer this question"
3. Match the language and tone of the user's question
4. Do not preface with "based on the context"""

        user_message = f"""Context: {context}
        
Query: {query}"""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def query(self, question: str, top_k: int = 5, document_id: int = None, model: str = "gpt-4o-mini") -> Dict:
        """
        Create a complete RAG query
                
        args:
            question: user query
            top_k: number of relevant chunks to consider
            document_id: to provide only if it's needed to limit the research to a certain document
            
        returns:
            dict with answer and metadata
        """
        # Search for relevant chunks
        search_results = self.searcher.search(
            query=question,
            top_k=top_k,
            document_id=document_id
        )
        
        if not search_results:
            return {
                "answer": "I don't have enough information to answer this question",
                "sources": [],
                "query": question
            }
        
        # avoid calling the model if there are not relevant chunks
        if (search_results[0]["similarity"] <= 0.3):
            return {
                "answer": "I don't have enough information to answer this question",
                "sources": [],
                "query": question
            }
        
        # Build context and prompt
        context = self.build_context(search_results)
        
        messages = self.build_prompt(question, context)
        
        # call the model
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": search_results,
                "query": question
            }
        
        sources = [
            {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"][:200] + "...",  # Preview
                "similarity": chunk["similarity"]
            }
            for chunk in search_results
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "query": question,
            "model_used": model
        }