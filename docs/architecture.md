# Architecture Overview

## System Architecture

The AI Research Trends RAG system follows a microservices architecture deployed on Azure Container Apps. The system is designed for scalability, observability, and maintainability.

## High-Level Components

### 1. Data Ingestion Layer
- **Azure Functions**: Serverless functions for periodic data ingestion
  - arXiv API ingestion (timer-triggered, weekly)
  - Semantic Scholar API enrichment
- **Azure Service Bus**: Message queue for reliable paper processing

### 2. Processing Layer
- **Processing Service**: Consumes messages, generates embeddings, stores data
- **Trend Analysis Service**: Computes research trends and topic clusters

### 3. Application Layer
- **RAG Query Service**: Handles user queries with retrieval + generation
- **API Gateway**: Routes requests, handles caching and rate limiting
- **Streamlit Frontend**: User interface

### 4. Data Layer
- **Qdrant**: Vector database for semantic search
- **Azure Cosmos DB**: NoSQL database for metadata and trends
- **Azure Blob Storage**: Storage for PDFs and exports
- **Azure Cache for Redis**: Response caching

### 5. Observability Layer
- **Opik**: LLM-specific tracing and evaluation
- **Azure Monitor**: Infrastructure monitoring and alerting

## Data Flow

### Ingestion Flow
1. Timer trigger activates Azure Function
2. Function queries arXiv and Semantic Scholar APIs
3. Raw paper data published to Service Bus queue
4. Processing Service consumes messages
5. Embeddings generated and stored in Qdrant
6. Metadata stored in Cosmos DB

### Query Flow
1. User submits query via Streamlit UI
2. Request routed through API Gateway
3. Cache check (Redis)
4. If cache miss:
   - Generate query embedding
   - Vector search in Qdrant
   - Keyword search in Cosmos DB
   - Re-rank results
   - Generate response with GPT-4
5. Response cached and returned
6. All LLM calls traced in Opik

## Technology Stack

- **Language**: Python 3.11+
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Qdrant
- **Database**: Azure Cosmos DB (NoSQL)
- **Cache**: Azure Cache for Redis
- **Queue**: Azure Service Bus
- **Compute**: Azure Container Apps
- **Storage**: Azure Blob Storage
- **Observability**: Opik + Azure Monitor
- **Frontend**: Streamlit
- **API**: FastAPI

## Scalability Considerations

- Container Apps auto-scale based on HTTP requests
- Qdrant HNSW index for fast vector search
- Redis caching reduces LLM API calls
- Service Bus ensures reliable message delivery
- Cosmos DB supports horizontal scaling

## Security

- Secrets stored in Azure Key Vault
- Managed identities for Azure resource access
- CORS configured on API Gateway
- Rate limiting to prevent abuse
- No authentication in MVP (single user mode)
