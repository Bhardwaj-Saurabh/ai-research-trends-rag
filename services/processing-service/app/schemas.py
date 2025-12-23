"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Author(BaseModel):
    """Author information."""
    name: str
    affiliation: Optional[str] = None


class PaperInput(BaseModel):
    """Input schema for paper ingestion."""
    paper_id: str = Field(..., description="Unique paper identifier (arXiv ID)")
    title: str
    authors: List[str]
    abstract: str
    published_date: str
    arxiv_url: str
    pdf_url: Optional[str] = None
    categories: List[str] = []

    # Optional Semantic Scholar data
    semantic_scholar_id: Optional[str] = None
    semantic_scholar_url: Optional[str] = None
    venue: Optional[str] = None
    citation_count: int = 0


class PaperMetadata(BaseModel):
    """Paper metadata stored in database."""
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: str
    arxiv_url: str
    pdf_url: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    semantic_scholar_url: Optional[str] = None
    venue: Optional[str] = None
    citation_count: int = 0
    citations_per_month: float = 0.0
    categories: List[str] = []
    keywords: List[str] = []
    ingested_at: str
    updated_at: str


class ProcessingResponse(BaseModel):
    """Response after processing a paper."""
    paper_id: str
    status: str
    message: str
    embedding_dimension: int
    stored_in_qdrant: bool
    stored_in_cosmos: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    qdrant_connected: bool
    cosmos_connected: bool
    timestamp: str
