"""Configuration settings for the Processing Service."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Qdrant Configuration
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "papers"

    # Azure Cosmos DB Configuration (optional for local dev)
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_database: str = "ai-research-db"
    cosmos_container: str = "papers"

    # Azure Service Bus Configuration (optional for local dev)
    servicebus_connection_string: str = ""
    servicebus_queue_name: str = "paper-ingestion-queue"

    # Application Settings
    log_level: str = "INFO"
    environment: str = "development"
    batch_size: int = 10

    # Opik Configuration
    opik_api_key: str = ""
    opik_workspace: str = "ai-research-trends"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
