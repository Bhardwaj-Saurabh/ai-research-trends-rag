"""Configuration settings for the RAG Query Service."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7

    # Qdrant Configuration
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "papers"

    # Retrieval Configuration
    top_k_retrieval: int = 10
    top_k_rerank: int = 5
    similarity_threshold: float = 0.7

    # Application Settings
    log_level: str = "INFO"
    environment: str = "development"

    # Opik Configuration
    opik_api_key: str = ""
    opik_workspace: str = "ai-research-trends"
    enable_opik: bool = False  # Set to True when Opik is configured

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
