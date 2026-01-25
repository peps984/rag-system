import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """
    Complete RAG system end-to-end test
    """
    print("Starting RAG System Test\n")
    
    # 1. Health check
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("Health check passed\n")
    
    # 2. Upload document
    print("Uploading test document...")
    test_content = """
    Python is a versatile and powerful programming language.
    Python is used for web development, data science, machine learning, and automation.
    Python's syntax is simple and readable.
    Python has a large community and many available libraries.
    The language was created by Guido van Rossum in 1991.
    Python supports multiple programming paradigms including object-oriented and functional programming.
    """
    
    with open("test_doc.txt", "w") as f:
        f.write(test_content)
    
    with open("test_doc.txt", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            files={"file": ("test_doc.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    doc_data = response.json()
    doc_id = doc_data["id"]
    print(f"Document uploaded (ID: {doc_id})\n")
    
    # Wait a moment to ensure everything is processed
    time.sleep(2)
    
    # 3. Test search
    print("Testing similarity search...")
    response = requests.post(
        f"{BASE_URL}/search",
        params={"query": "Python features", "top_k": 3}
    )
    assert response.status_code == 200
    search_data = response.json()
    assert len(search_data["results"]) > 0
    print(f"Search returned {len(search_data['results'])} results\n")
    
    # Print top result
    if search_data["results"]:
        top_result = search_data["results"][0]
        print(f"Top result similarity: {top_result['similarity']:.2f}")
        print(f"Content preview: {top_result['content'][:100]}...\n")
    
    # 4. Test RAG query
    print("Testing RAG query...")
    response = requests.post(
        f"{BASE_URL}/query",
        params={"question": "What are the main characteristics of Python?"}
    )
    assert response.status_code == 200
    rag_data = response.json()
    assert len(rag_data["answer"]) > 0
    print(f"✅ RAG query successful\n")
    print(f"Question: {rag_data['query']}")
    print(f"Answer: {rag_data['answer']}\n")
    print(f"Number of sources: {len(rag_data['sources'])}\n")
    
    # 5. Test another query
    print("Testing second query...")
    response = requests.post(
        f"{BASE_URL}/query",
        params={"question": "Who created Python and when?"}
    )
    assert response.status_code == 200
    rag_data2 = response.json()
    print(f"Question: {rag_data2['query']}")
    print(f"Answer: {rag_data2['answer']}\n")
    
    # 6. Test search with minimum similarity threshold
    print("Testing search with similarity threshold...")
    response = requests.post(
        f"{BASE_URL}/search",
        params={"query": "programming paradigms", "top_k": 5, "min_similarity": 0.4}
    )
    assert response.status_code == 200
    search_data = response.json()
    print(f"Found {len(search_data['results'])} results with similarity > 0.4\n")
    
    # 7. Cleanup
    print("Cleaning up...")
    response = requests.delete(f"{BASE_URL}/documents/{doc_id}")
    assert response.status_code == 200
    print("Test document deleted from server db\n")
    
    print("=" * 60)
    print("🎉 All tests passed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_complete_flow()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure the API is running on http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to {BASE_URL}")
        print("Make sure the API is running with: docker compose up -d")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")