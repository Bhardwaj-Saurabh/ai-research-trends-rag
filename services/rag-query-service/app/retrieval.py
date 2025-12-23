"""Retrieval logic for searching papers in Qdrant."""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from openai import OpenAI
from app.config import Settings
from app.schemas import PaperSource

logger = logging.getLogger(__name__)


class PaperRetriever:
    """Handles paper retrieval from Qdrant."""

    def __init__(self, settings: Settings):
        """Initialize the retriever."""
        self.settings = settings
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.collection_name = settings.qdrant_collection_name

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.

        Args:
            query: User's search query

        Returns:
            Query embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                input=query,
                model=self.settings.openai_embedding_model
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated query embedding with dimension: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise

    def search_papers(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar papers in Qdrant.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional search filters

        Returns:
            List of matching papers with metadata
        """
        try:
            # Perform vector search
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=self.settings.similarity_threshold
            )

            papers = []
            for result in results:
                paper = {
                    "score": result.score,
                    **result.payload
                }
                papers.append(paper)

            logger.info(f"Retrieved {len(papers)} papers from Qdrant")
            return papers

        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}")
            raise

    def rerank_papers(
        self,
        query: str,
        papers: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simple re-ranking based on multiple criteria.

        For MVP, we'll use a simple scoring function. In production,
        you could use a cross-encoder model for better re-ranking.

        Args:
            query: Original query
            papers: Retrieved papers
            top_k: Number of papers to return after re-ranking

        Returns:
            Re-ranked papers
        """
        try:
            query_lower = query.lower()

            for paper in papers:
                # Start with similarity score
                final_score = paper['score']

                # Boost if query terms appear in title (simple keyword matching)
                title_lower = paper.get('title', '').lower()
                query_words = set(query_lower.split())
                title_words = set(title_lower.split())
                overlap = len(query_words & title_words)
                if overlap > 0:
                    final_score += 0.1 * overlap

                # Boost based on citation count (normalized)
                citation_count = paper.get('citation_count', 0)
                if citation_count > 0:
                    citation_boost = min(citation_count / 1000, 0.2)  # Max boost of 0.2
                    final_score += citation_boost

                paper['final_score'] = final_score

            # Sort by final score
            reranked = sorted(papers, key=lambda x: x['final_score'], reverse=True)

            logger.info(f"Re-ranked papers, returning top {top_k}")
            return reranked[:top_k]

        except Exception as e:
            logger.error(f"Error re-ranking papers: {str(e)}")
            return papers[:top_k]  # Fallback to original order

    def format_as_paper_sources(self, papers: List[Dict[str, Any]]) -> List[PaperSource]:
        """
        Convert retrieved papers to PaperSource schema.

        Args:
            papers: Retrieved papers

        Returns:
            List of PaperSource objects
        """
        sources = []
        for paper in papers:
            try:
                source = PaperSource(
                    paper_id=paper.get('paper_id', ''),
                    title=paper.get('title', ''),
                    authors=paper.get('authors', []),
                    abstract=paper.get('abstract', '')[:500],  # Truncate for response
                    published_date=paper.get('published_date', ''),
                    arxiv_url=paper.get('arxiv_url', ''),
                    citation_count=paper.get('citation_count', 0),
                    relevance_score=round(paper.get('final_score', paper.get('score', 0)), 3),
                    venue=paper.get('venue')
                )
                sources.append(source)
            except Exception as e:
                logger.error(f"Error formatting paper source: {str(e)}")
                continue

        return sources

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PaperSource]:
        """
        Main retrieval pipeline: embed query, search, re-rank.

        Args:
            query: User's search query
            top_k: Number of final results
            filters: Optional search filters

        Returns:
            List of relevant papers as PaperSource objects
        """
        logger.info(f"Starting retrieval for query: {query}")

        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)

        # Retrieve more papers than needed for re-ranking
        retrieval_k = min(top_k * 2, self.settings.top_k_retrieval)
        papers = self.search_papers(query_embedding, retrieval_k, filters)

        if not papers:
            logger.warning("No papers retrieved from Qdrant")
            return []

        # Re-rank papers
        reranked_papers = self.rerank_papers(query, papers, top_k)

        # Format as PaperSource objects
        sources = self.format_as_paper_sources(reranked_papers)

        logger.info(f"Retrieval complete. Returning {len(sources)} papers")
        return sources
