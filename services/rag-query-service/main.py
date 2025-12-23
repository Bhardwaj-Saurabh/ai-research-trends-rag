"""RAG Query Service - Main FastAPI application."""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import Settings, get_settings
from app.schemas import QueryRequest, QueryResponse, HealthResponse
from app.retrieval import PaperRetriever
from app.generation import ResponseGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
retriever = None
generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global retriever, generator

    logger.info("Starting RAG Query Service...")
    settings = get_settings()

    # Initialize services
    retriever = PaperRetriever(settings)
    generator = ResponseGenerator(settings)

    logger.info("RAG Query Service started successfully")
    yield

    # Cleanup
    logger.info("Shutting down RAG Query Service...")


# Create FastAPI app
app = FastAPI(
    title="AI Research Trends - RAG Query Service",
    description="Answers research questions using RAG over AI research papers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "RAG Query Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint."""
    qdrant_ok = False
    openai_ok = bool(settings.openai_api_key)

    try:
        # Test Qdrant connection
        collections = retriever.qdrant_client.get_collections()
        qdrant_ok = True
        logger.info(f"Qdrant health check passed. Collections: {len(collections.collections)}")
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")

    status = "healthy" if (qdrant_ok and openai_ok) else "unhealthy"

    return HealthResponse(
        status=status,
        service="rag-query-service",
        qdrant_connected=qdrant_ok,
        openai_configured=openai_ok,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/query", response_model=QueryResponse)
async def query_papers(
    request: QueryRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Answer a research question using RAG.

    This endpoint:
    1. Retrieves relevant papers from the vector database
    2. Generates a contextualized answer using GPT-4
    3. Returns the answer with source citations

    Args:
        request: Query request with question and filters

    Returns:
        Generated answer with source papers
    """
    try:
        logger.info(f"Received query: {request.query}")
        start_time = datetime.utcnow()

        # Retrieve relevant papers
        papers = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters.model_dump() if request.filters else None
        )

        if not papers:
            return QueryResponse(
                query=request.query,
                answer="I couldn't find any relevant research papers to answer your question. Try rephrasing your query or broadening your search criteria.",
                sources=[],
                metadata={
                    "papers_found": 0,
                    "processing_time_ms": 0
                }
            )

        # Generate response
        answer, gen_metadata = generator.generate_response(
            query=request.query,
            papers=papers
        )

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Build response metadata
        metadata = {
            **gen_metadata,
            "processing_time_ms": processing_time_ms,
            "retrieval_top_k": request.top_k,
            "timestamp": end_time.isoformat()
        }

        logger.info(f"Query processed successfully in {processing_time_ms}ms")

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=papers if request.include_sources else [],
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get service statistics."""
    try:
        info = retriever.qdrant_client.get_collection(retriever.collection_name)
        return {
            "collection": retriever.collection_name,
            "points_count": info.points_count if hasattr(info, 'points_count') else 0,
            "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
