"""Storage layer for Qdrant and Cosmos DB."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from app.config import Settings
from app.schemas import PaperMetadata

logger = logging.getLogger(__name__)


class QdrantStorage:
    """Qdrant vector database storage."""

    def __init__(self, settings: Settings):
        """Initialize Qdrant client."""
        self.settings = settings
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        self.collection_name = settings.qdrant_collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")
            raise

    def check_paper_exists(self, paper_id: str) -> bool:
        """
        Check if a paper already exists in the collection.

        Args:
            paper_id: Paper identifier

        Returns:
            True if paper exists, False otherwise
        """
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="paper_id",
                            match=MatchValue(value=paper_id)
                        )
                    ]
                ),
                limit=1
            )
            exists = len(results[0]) > 0
            if exists:
                logger.info(f"Paper {paper_id} already exists in Qdrant")
            return exists
        except Exception as e:
            logger.error(f"Error checking if paper exists: {str(e)}")
            return False

    def store_paper(
        self,
        paper_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Store paper embedding and metadata in Qdrant.

        Args:
            paper_id: Unique paper identifier
            embedding: Vector embedding
            metadata: Paper metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if paper already exists
            if self.check_paper_exists(paper_id):
                logger.info(f"Skipping duplicate paper: {paper_id}")
                return False

            # Create point
            point = PointStruct(
                id=hash(paper_id) & 0xFFFFFFFFFFFFFFFF,  # Convert to unsigned 64-bit int
                vector=embedding,
                payload=metadata
            )

            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            logger.info(f"Stored paper {paper_id} in Qdrant")
            return True
        except Exception as e:
            logger.error(f"Error storing paper in Qdrant: {str(e)}")
            raise

    def search_papers(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar papers.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters

        Returns:
            List of matching papers with scores
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            papers = []
            for result in results:
                paper = {
                    "score": result.score,
                    **result.payload
                }
                papers.append(paper)

            logger.info(f"Found {len(papers)} similar papers")
            return papers
        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size if hasattr(info.config.params, 'vectors') else 0,
                "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else 0,
                "points_count": info.points_count if hasattr(info, 'points_count') else 0,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}


class CosmosStorage:
    """Azure Cosmos DB storage (optional for local development)."""

    def __init__(self, settings: Settings):
        """Initialize Cosmos DB client."""
        self.settings = settings
        self.enabled = bool(settings.cosmos_endpoint and settings.cosmos_key)

        if self.enabled:
            from azure.cosmos import CosmosClient
            self.client = CosmosClient(
                settings.cosmos_endpoint,
                settings.cosmos_key
            )
            self.database = self.client.get_database_client(settings.cosmos_database)
            self.container = self.database.get_container_client(settings.cosmos_container)
            logger.info("Cosmos DB client initialized")
        else:
            logger.warning("Cosmos DB not configured - running in local mode")
            self.client = None

    def store_paper_metadata(self, metadata: PaperMetadata) -> bool:
        """
        Store paper metadata in Cosmos DB.

        Args:
            metadata: Paper metadata

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Cosmos DB not enabled - skipping metadata storage")
            return False

        try:
            item = metadata.model_dump()
            item['id'] = metadata.paper_id
            self.container.upsert_item(item)
            logger.info(f"Stored metadata for paper {metadata.paper_id} in Cosmos DB")
            return True
        except Exception as e:
            logger.error(f"Error storing metadata in Cosmos DB: {str(e)}")
            return False

    def get_paper_metadata(self, paper_id: str) -> Optional[PaperMetadata]:
        """Get paper metadata from Cosmos DB."""
        if not self.enabled:
            return None

        try:
            item = self.container.read_item(
                item=paper_id,
                partition_key=paper_id
            )
            return PaperMetadata(**item)
        except Exception as e:
            logger.error(f"Error getting metadata from Cosmos DB: {str(e)}")
            return None
