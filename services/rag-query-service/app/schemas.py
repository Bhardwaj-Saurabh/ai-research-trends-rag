"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QueryFilters(BaseModel):
    """Filters for search queries."""
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_citations: Optional[int] = 0
    categories: Optional[List[str]] = []
    venues: Optional[List[str]] = []


class QueryRequest(BaseModel):
    """Request schema for RAG queries."""
    query: str = Field(..., min_length=3, description="User's research question")
    filters: Optional[QueryFilters] = None
    top_k: int = Field(5, ge=1, le=20, description="Number of papers to retrieve")
    include_sources: bool = Field(True, description="Include source papers in response")


class PaperSource(BaseModel):
    """Source paper information."""
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: str
    arxiv_url: str
    citation_count: int = 0
    relevance_score: float
    venue: Optional[str] = None


class QueryResponse(BaseModel):
    """Response schema for RAG queries."""
    query: str
    answer: str
    sources: List[PaperSource]
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    qdrant_connected: bool
    openai_configured: bool
    timestamp: str
