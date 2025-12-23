"""OpenAI embeddings generation."""
import logging
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import Settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using OpenAI API."""

    def __init__(self, settings: Settings):
        """Initialize the embedding generator."""
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    def create_paper_text(self, title: str, abstract: str) -> str:
        """
        Combine title and abstract for embedding.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Combined text for embedding
        """
        return f"Title: {title}\n\nAbstract: {abstract}"
