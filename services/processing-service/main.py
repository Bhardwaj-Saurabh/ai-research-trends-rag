"""Processing Service - Main FastAPI application."""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import Settings, get_settings
from app.schemas import (
    PaperInput,
    PaperMetadata,
    ProcessingResponse,
    HealthResponse
)
from app.embeddings import EmbeddingGenerator
from app.storage import QdrantStorage, CosmosStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
embedding_generator = None
qdrant_storage = None
cosmos_storage = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global embedding_generator, qdrant_storage, cosmos_storage

    logger.info("Starting Processing Service...")
    settings = get_settings()

    # Initialize services
    embedding_generator = EmbeddingGenerator(settings)
    qdrant_storage = QdrantStorage(settings)
    cosmos_storage = CosmosStorage(settings)

    logger.info("Processing Service started successfully")
    yield

    # Cleanup
    logger.info("Shutting down Processing Service...")


# Create FastAPI app
app = FastAPI(
    title="AI Research Trends - Processing Service",
    description="Processes research papers, generates embeddings, and stores them in vector database",
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
        "service": "Processing Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    qdrant_ok = False
    cosmos_ok = False

    try:
        # Check Qdrant connection
        info = qdrant_storage.get_collection_info()
        qdrant_ok = True
        logger.info(f"Qdrant health check passed: {info}")
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")

    try:
        # Check Cosmos DB connection (if enabled)
        if cosmos_storage.enabled:
            cosmos_ok = True
        else:
            cosmos_ok = True  # Not enabled, so consider it OK
    except Exception as e:
        logger.error(f"Cosmos DB health check failed: {str(e)}")

    status = "healthy" if qdrant_ok else "unhealthy"

    return HealthResponse(
        status=status,
        service="processing-service",
        qdrant_connected=qdrant_ok,
        cosmos_connected=cosmos_ok,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/process", response_model=ProcessingResponse)
async def process_paper(
    paper: PaperInput,
    settings: Settings = Depends(get_settings)
):
    """
    Process a research paper: generate embedding and store in databases.

    Args:
        paper: Paper information

    Returns:
        Processing response with status
    """
    try:
        logger.info(f"Processing paper: {paper.paper_id} - {paper.title}")

        # Check if paper already exists
        if qdrant_storage.check_paper_exists(paper.paper_id):
            return ProcessingResponse(
                paper_id=paper.paper_id,
                status="skipped",
                message="Paper already exists in database",
                embedding_dimension=settings.embedding_dimension,
                stored_in_qdrant=False,
                stored_in_cosmos=False
            )

        # Generate embedding
        paper_text = embedding_generator.create_paper_text(
            paper.title,
            paper.abstract
        )
        embedding = embedding_generator.generate_embedding(paper_text)

        # Prepare metadata
        now = datetime.utcnow().isoformat()

        # Calculate citations per month (if citation count available)
        citations_per_month = 0.0
        if paper.citation_count > 0:
            try:
                pub_date = datetime.fromisoformat(paper.published_date.replace('Z', '+00:00'))
                months_since_pub = max((datetime.utcnow() - pub_date).days / 30, 1)
                citations_per_month = paper.citation_count / months_since_pub
            except Exception as e:
                logger.warning(f"Could not calculate citations per month: {str(e)}")

        metadata_dict = {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract[:500],  # Store truncated abstract in Qdrant
            "published_date": paper.published_date,
            "arxiv_url": paper.arxiv_url,
            "pdf_url": paper.pdf_url or "",
            "semantic_scholar_id": paper.semantic_scholar_id or "",
            "semantic_scholar_url": paper.semantic_scholar_url or "",
            "venue": paper.venue or "",
            "citation_count": paper.citation_count,
            "citations_per_month": round(citations_per_month, 2),
            "categories": paper.categories,
            "keywords": [],  # TODO: Extract keywords
            "ingested_at": now,
            "updated_at": now
        }

        # Store in Qdrant
        stored_in_qdrant = qdrant_storage.store_paper(
            paper_id=paper.paper_id,
            embedding=embedding,
            metadata=metadata_dict
        )

        # Store in Cosmos DB (if enabled)
        stored_in_cosmos = False
        if cosmos_storage.enabled:
            paper_metadata = PaperMetadata(**metadata_dict)
            stored_in_cosmos = cosmos_storage.store_paper_metadata(paper_metadata)

        logger.info(
            f"Successfully processed paper {paper.paper_id}. "
            f"Qdrant: {stored_in_qdrant}, Cosmos: {stored_in_cosmos}"
        )

        return ProcessingResponse(
            paper_id=paper.paper_id,
            status="success",
            message="Paper processed and stored successfully",
            embedding_dimension=len(embedding),
            stored_in_qdrant=stored_in_qdrant,
            stored_in_cosmos=stored_in_cosmos
        )

    except Exception as e:
        logger.error(f"Error processing paper {paper.paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    try:
        info = qdrant_storage.get_collection_info()
        return {
            "collection": qdrant_storage.collection_name,
            "statistics": info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
