"""
Simple test script to verify the services are working correctly.
Run this after starting the processing service and ingesting some papers.
"""
import requests
import json
import sys
from time import sleep


def test_processing_service(base_url="http://localhost:8000"):
    """Test the processing service."""
    print("\n" + "="*60)
    print("Testing Processing Service")
    print("="*60)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        print(f"✓ Service is {health['status']}")
        print(f"  - Qdrant connected: {health['qdrant_connected']}")
        print(f"  - Cosmos connected: {health['cosmos_connected']}")
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False

    # Test stats endpoint
    print("\n2. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        response.raise_for_status()
        stats = response.json()
        print(f"✓ Collection stats retrieved")
        print(f"  - Collection: {stats.get('collection', 'N/A')}")
        print(f"  - Statistics: {stats.get('statistics', {})}")
    except Exception as e:
        print(f"✗ Stats check failed: {str(e)}")

    return True


def test_rag_query_service(base_url="http://localhost:8001"):
    """Test the RAG query service."""
    print("\n" + "="*60)
    print("Testing RAG Query Service")
    print("="*60)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        print(f"✓ Service is {health['status']}")
        print(f"  - Qdrant connected: {health['qdrant_connected']}")
        print(f"  - OpenAI configured: {health['openai_configured']}")
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False

    # Test query endpoint with a sample query
    print("\n2. Testing query endpoint...")
    try:
        query_data = {
            "query": "What are the latest developments in transformer models?",
            "top_k": 3,
            "include_sources": True
        }

        print(f"   Query: \"{query_data['query']}\"")
        print("   Waiting for response (this may take 5-10 seconds)...")

        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        print(f"\n✓ Query successful!")
        print(f"\n   Answer:")
        print(f"   {result['answer'][:300]}...")

        print(f"\n   Sources ({len(result['sources'])} papers):")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"   {i}. {source['title'][:60]}...")
            print(f"      Relevance: {source['relevance_score']:.3f}")

        print(f"\n   Metadata:")
        metadata = result.get('metadata', {})
        print(f"   - Processing time: {metadata.get('processing_time_ms', 0)}ms")
        print(f"   - Tokens used: {metadata.get('tokens_used', 0)}")

    except Exception as e:
        print(f"✗ Query failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Error details: {e.response.text}")
        return False

    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI Research Trends RAG - Service Tests")
    print("="*60)

    print("\nThis script will test the following services:")
    print("1. Processing Service (port 8000)")
    print("2. RAG Query Service (port 8001)")
    print("\nMake sure both services are running before continuing.")

    input("\nPress Enter to start tests...")

    # Test Processing Service
    processing_ok = test_processing_service()

    if not processing_ok:
        print("\n⚠️  Processing service tests failed. Check if the service is running.")
        print("   Start it with: cd services/processing-service && uvicorn main:app --reload")
        sys.exit(1)

    # Wait a bit
    sleep(1)

    # Test RAG Query Service
    rag_ok = test_rag_query_service()

    if not rag_ok:
        print("\n⚠️  RAG Query service tests failed. Check if the service is running.")
        print("   Start it with: cd services/rag-query-service && uvicorn main:app --reload --port 8001")
        sys.exit(1)

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✓ Processing Service: {'PASSED' if processing_ok else 'FAILED'}")
    print(f"✓ RAG Query Service: {'PASSED' if rag_ok else 'FAILED'}")
    print("\n🎉 All tests passed! Your services are working correctly.")
    print("\nNext steps:")
    print("1. Ingest more papers: python scripts/ingest_arxiv_papers.py --max-results 50")
    print("2. Try different queries through the API")
    print("3. Build the Streamlit frontend for a better user experience")
    print("\n")


if __name__ == "__main__":
    main()
