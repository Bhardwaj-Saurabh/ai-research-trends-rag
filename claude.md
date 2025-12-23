# AI Research Trends RAG - Implementation Plan

## 1. Executive Summary

**Project Name:** AI Research Trends Discovery Platform
**Architecture:** Microservices on Azure Container Apps
**Scale Target:** MVP with ~1,000 papers, weekly ingestion
**Learning Focus:** End-to-end RAG, Azure cloud services, observability, microservices

**Core Value Proposition:**
Transform weeks of research paper exploration into minutes with AI-powered discovery, trend analysis, and citation-backed insights.

---

## 2. Enhanced Vision & Features

### 2.1 Core Features (MVP)
- ✅ Natural language Q&A over AI research papers
- ✅ Semantic + keyword hybrid search
- ✅ Emerging trend detection (30/90/180 day windows)
- ✅ Citation-aware paper ranking
- ✅ Time-based filtering
- ✅ Paper metadata (authors, venue, citations, abstract)
- ✅ Source attribution with direct arXiv/Semantic Scholar links

### 2.2 Enhanced UX Features
- **Smart Summarization:** Auto-generate paper summaries using LLM
- **Visual Trend Timeline:** Interactive charts showing trend growth over time
- **Related Papers:** Show similar papers based on embeddings
- **Export Capabilities:** Download citations in BibTeX, RIS, or markdown formats
- **Query History:** Save and revisit previous searches
- **Advanced Filters:**
  - Filter by venue (NeurIPS, ICML, ICLR, arXiv categories)
  - Filter by author
  - Filter by citation count (high-impact papers)
  - Filter by publication date range
- **Paper Comparison:** Side-by-side comparison of multiple papers
- **Weekly Digest:** Automated trend summaries (future feature)
- **Impact Indicators:** Show citation velocity (citations per month since publication)

### 2.3 Technical Enhancements
- **Hybrid Search:** Combine semantic (vector) + keyword (BM25) for better retrieval
- **Re-ranking:** Use cross-encoder models to re-rank top results
- **Query Expansion:** Automatically expand queries with synonyms/related terms
- **Caching:** Cache frequent queries to reduce latency and costs
- **Rate Limiting:** Protect APIs from abuse
- **Health Checks:** Comprehensive service health monitoring
- **Graceful Degradation:** Fallback mechanisms when services are unavailable

---

## 3. System Architecture

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         AZURE CLOUD                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Data Ingestion Layer                     │  │
│  │                                                            │  │
│  │  ┌─────────────┐      ┌──────────────┐                   │  │
│  │  │ Azure Func  │      │ Azure Func   │                   │  │
│  │  │ arXiv       │      │ Semantic     │                   │  │
│  │  │ Ingestion   │      │ Scholar      │                   │  │
│  │  │ (Timer)     │      │ Ingestion    │                   │  │
│  │  └──────┬──────┘      └──────┬───────┘                   │  │
│  │         │                     │                            │  │
│  │         └─────────┬───────────┘                            │  │
│  │                   ▼                                        │  │
│  │         ┌─────────────────────┐                           │  │
│  │         │ Azure Service Bus   │                           │  │
│  │         │ (Message Queue)     │                           │  │
│  │         └──────────┬──────────┘                           │  │
│  └────────────────────┼──────────────────────────────────────┘  │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Processing Layer (Container Apps)            │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  Paper Processing Service                    │         │  │
│  │  │  - Extract metadata                          │         │  │
│  │  │  - Generate embeddings (OpenAI)             │         │  │
│  │  │  - Detect duplicates                         │         │  │
│  │  │  - Store in Qdrant + Cosmos DB              │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  Trend Analysis Service                      │         │  │
│  │  │  - Compute keyword frequency                 │         │  │
│  │  │  - Cluster topics                            │         │  │
│  │  │  - Calculate growth metrics                  │         │  │
│  │  │  - Store trend data                          │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Application Layer (Container Apps)           │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  RAG Query Service (FastAPI)                 │         │  │
│  │  │  - Query understanding                       │         │  │
│  │  │  - Hybrid retrieval (Qdrant + metadata)     │         │  │
│  │  │  - Re-ranking                                │         │  │
│  │  │  - Response generation (OpenAI)              │         │  │
│  │  │  - Citation management                       │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  API Gateway Service (FastAPI)               │         │  │
│  │  │  - Request routing                           │         │  │
│  │  │  - Rate limiting                             │         │  │
│  │  │  - Response caching                          │         │  │
│  │  │  - CORS handling                             │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  Streamlit Frontend (Container App)          │         │  │
│  │  │  - Search interface                          │         │  │
│  │  │  - Trend visualizations                      │         │  │
│  │  │  - Paper details & comparison                │         │  │
│  │  │  - Export features                           │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Data Layer                              │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ Qdrant       │  │ Azure Cosmos │  │ Azure Blob   │   │  │
│  │  │ Vector DB    │  │ DB (NoSQL)   │  │ Storage      │   │  │
│  │  │ (Container)  │  │ - Metadata   │  │ - PDFs       │   │  │
│  │  │ - Embeddings │  │ - Trends     │  │ - Exports    │   │  │
│  │  │ - Search     │  │ - Cache      │  │              │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Observability Layer (Opik)                  │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  Opik Tracing & Evaluation                   │         │  │
│  │  │  - LLM call tracing                          │         │  │
│  │  │  - Latency monitoring                        │         │  │
│  │  │  - Cost tracking                             │         │  │
│  │  │  - Quality evaluation (relevance, accuracy)  │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────┐         │  │
│  │  │  Azure Monitor + Application Insights        │         │  │
│  │  │  - Service health                            │         │  │
│  │  │  - Performance metrics                       │         │  │
│  │  │  - Error tracking                            │         │  │
│  │  └─────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

External APIs:
- OpenAI API (embeddings + LLM)
- arXiv API
- Semantic Scholar API
```

### 3.2 Microservices Breakdown

#### Service 1: Ingestion Service (Azure Functions)
- **Responsibility:** Fetch papers from arXiv and Semantic Scholar
- **Trigger:** Timer trigger (weekly) or manual HTTP trigger
- **Tech Stack:** Python, Azure Functions, Azure Service Bus
- **Key Operations:**
  - Query arXiv API for new AI papers
  - Query Semantic Scholar API for citation data
  - Publish messages to Service Bus queue
  - Handle API rate limits and retries
- **Outputs:** Raw paper metadata to Service Bus

#### Service 2: Processing Service (Container App)
- **Responsibility:** Process raw papers and generate embeddings
- **Tech Stack:** Python, FastAPI, OpenAI SDK, Qdrant client
- **Key Operations:**
  - Consume messages from Service Bus
  - Parse and normalize paper metadata
  - Generate embeddings using OpenAI text-embedding-3-small
  - Detect and skip duplicates
  - Store vectors in Qdrant
  - Store metadata in Cosmos DB
  - Trigger trend analysis
- **Outputs:** Searchable papers in Qdrant + Cosmos DB

#### Service 3: Trend Analysis Service (Container App)
- **Responsibility:** Compute research trends and topic clusters
- **Tech Stack:** Python, scikit-learn, pandas
- **Key Operations:**
  - Extract keywords from abstracts (TF-IDF, KeyBERT)
  - Compute keyword frequency over time windows
  - Cluster papers by topic (HDBSCAN on embeddings)
  - Calculate trend growth rates
  - Store trend data in Cosmos DB
- **Outputs:** Trend data (keywords, growth rates, clusters)

#### Service 4: RAG Query Service (Container App)
- **Responsibility:** Handle user queries and generate responses
- **Tech Stack:** Python, FastAPI, LangChain/LlamaIndex, OpenAI SDK
- **Key Operations:**
  - Parse and expand user queries
  - Hybrid retrieval (vector search + keyword search)
  - Re-rank results using cross-encoder
  - Generate contextualized responses using GPT-4
  - Format citations and references
  - Log traces to Opik
- **Inputs:** User query + filters
- **Outputs:** Generated answer + source papers + citations

#### Service 5: API Gateway (Container App)
- **Responsibility:** Route requests, handle cross-cutting concerns
- **Tech Stack:** Python, FastAPI
- **Key Operations:**
  - Request routing to appropriate services
  - Rate limiting (per-IP limits)
  - Response caching (Redis on Azure Cache for Redis)
  - CORS configuration
  - Health check aggregation
- **Endpoints:**
  - `/api/search` → RAG Query Service
  - `/api/trends` → Trend data from Cosmos DB
  - `/api/papers/{id}` → Paper details
  - `/health` → Aggregated health status

#### Service 6: Frontend (Streamlit on Container App)
- **Responsibility:** User interface
- **Tech Stack:** Python, Streamlit, Plotly, Pandas
- **Key Features:**
  - Search bar with natural language queries
  - Advanced filter panel (date, venue, citations, authors)
  - Results display with paper cards
  - Trend visualization (interactive line/bar charts)
  - Paper detail modal
  - Export buttons (BibTeX, markdown)
  - Query history sidebar

---

## 4. Data Flow

### 4.1 Ingestion Flow (Weekly)
```
1. Azure Function Timer Trigger (every Sunday 00:00 UTC)
2. Fetch papers from arXiv (cs.AI, cs.LG, cs.CL) from last 7 days
3. Fetch citation data from Semantic Scholar for each paper
4. Publish each paper as message to Azure Service Bus
5. Processing Service consumes messages (parallel processing)
6. For each paper:
   a. Check if paper already exists (by arXiv ID)
   b. Generate embedding of title + abstract
   c. Store vector in Qdrant with metadata
   d. Store full metadata in Cosmos DB
7. Trigger Trend Analysis Service (daily, after ingestion)
8. Compute trends and update Cosmos DB
```

### 4.2 Query Flow (User Search)
```
1. User enters query in Streamlit UI
2. Streamlit sends POST /api/search to API Gateway
3. API Gateway checks cache (Redis)
   - If cached → return cached response
   - If not cached → route to RAG Query Service
4. RAG Query Service:
   a. Generate query embedding (OpenAI)
   b. Vector search in Qdrant (top 50 results)
   c. Keyword search in Cosmos DB (BM25, top 50 results)
   d. Merge and re-rank (top 10 results)
   e. Build context from top 5 papers
   f. Generate response using GPT-4 with citations
   g. Log to Opik (trace, latency, tokens, cost)
5. API Gateway caches response and returns to Streamlit
6. Streamlit displays answer + cited papers
```

### 4.3 Trend Query Flow
```
1. User selects "Trending Topics" tab in UI
2. Streamlit sends GET /api/trends?window=30 to API Gateway
3. API Gateway queries Cosmos DB for precomputed trends
4. Return trends with growth metrics
5. Streamlit renders interactive charts (Plotly)
```

---

## 5. Technology Stack Details

### 5.1 Core Technologies

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **LLM** | OpenAI GPT-4 (via API) | High quality, well-documented, pay-as-you-go |
| **Embeddings** | OpenAI text-embedding-3-small | Cost-effective, 1536 dims, good performance |
| **Vector DB** | Qdrant (self-hosted) | Open source, excellent performance, learning experience |
| **Metadata DB** | Azure Cosmos DB (NoSQL) | Native Azure, flexible schema, global distribution |
| **Cache** | Azure Cache for Redis | Fast, managed, supports TTL |
| **Message Queue** | Azure Service Bus | Reliable, supports dead-letter queue, managed |
| **Functions** | Azure Functions (Python) | Serverless, timer triggers, cost-effective |
| **Containers** | Azure Container Apps | Managed Kubernetes, auto-scaling, simple deployment |
| **Container Registry** | Azure Container Registry | Native Azure, secure, geo-replication |
| **Storage** | Azure Blob Storage | Cheap, scalable, for PDFs and exports |
| **Observability** | Opik + Azure Monitor | LLM-specific tracing + general monitoring |
| **Frontend** | Streamlit | Rapid development, Python-native, good for demos |
| **API Framework** | FastAPI | Fast, async, auto-docs, type hints |
| **Orchestration** | LangChain or LlamaIndex | RAG abstractions, tooling, observability hooks |

### 5.2 Azure Services Overview

```
┌─────────────────────────────────────────────────────────┐
│ Azure Subscription                                      │
│                                                          │
│ Resource Group: rg-ai-research-trends-prod              │
│                                                          │
│ ├── Azure Container Registry (ACR)                      │
│ │   └── Container images for all services               │
│ │                                                        │
│ ├── Azure Container Apps Environment                    │
│ │   ├── qdrant-vectordb                                │
│ │   ├── processing-service                             │
│ │   ├── trend-analysis-service                         │
│ │   ├── rag-query-service                              │
│ │   ├── api-gateway                                    │
│ │   └── streamlit-frontend                             │
│ │                                                        │
│ ├── Azure Functions App                                 │
│ │   ├── arxiv-ingestion-function                       │
│ │   └── semantic-scholar-ingestion-function            │
│ │                                                        │
│ ├── Azure Cosmos DB                                     │
│ │   ├── Database: ai-research-db                       │
│ │   ├── Container: papers                              │
│ │   ├── Container: trends                              │
│ │   └── Container: query-cache                         │
│ │                                                        │
│ ├── Azure Service Bus Namespace                         │
│ │   ├── Queue: paper-ingestion-queue                   │
│ │   └── Queue: trend-analysis-queue                    │
│ │                                                        │
│ ├── Azure Cache for Redis                               │
│ │   └── For API response caching                       │
│ │                                                        │
│ ├── Azure Blob Storage                                  │
│ │   ├── Container: paper-pdfs                          │
│ │   └── Container: exports                             │
│ │                                                        │
│ ├── Azure Key Vault                                     │
│ │   └── Secrets (OpenAI API key, connection strings)   │
│ │                                                        │
│ └── Azure Monitor / Application Insights                │
│     └── Logs, metrics, dashboards                       │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Implementation Phases

### Phase 1: Foundation & Data Ingestion (Week 1-2)

**Goal:** Set up Azure infrastructure and basic ingestion pipeline

**Tasks:**
1. **Azure Setup**
   - Create resource group
   - Set up Azure Container Registry (ACR)
   - Create Azure Cosmos DB account + containers
   - Create Azure Service Bus namespace + queues
   - Set up Azure Key Vault with OpenAI API key

2. **Ingestion Service (Azure Function)**
   - Create Python Azure Function with timer trigger
   - Implement arXiv API client (query cs.AI, cs.LG, cs.CL)
   - Implement Semantic Scholar API client
   - Parse and normalize paper metadata
   - Publish to Service Bus queue
   - Add error handling and logging
   - Test with small batch (10 papers)

3. **Processing Service (Container App)**
   - Create FastAPI service with Service Bus consumer
   - Implement OpenAI embedding generation
   - Set up Qdrant container on Azure Container Apps
   - Implement vector storage logic
   - Implement metadata storage in Cosmos DB
   - Add duplicate detection
   - Containerize with Dockerfile
   - Push to ACR and deploy to Container Apps

**Deliverables:**
- ✅ Working ingestion pipeline (arXiv → Service Bus → Processing → Qdrant + Cosmos)
- ✅ ~100 papers ingested for testing
- ✅ Basic monitoring with Azure Monitor

---

### Phase 2: RAG Query Service (Week 3-4)

**Goal:** Build core retrieval and generation capabilities

**Tasks:**
1. **RAG Query Service**
   - Create FastAPI service for queries
   - Implement query embedding generation
   - Implement vector search in Qdrant (top-k retrieval)
   - Implement metadata filtering (date, venue, citations)
   - Implement hybrid search (vector + keyword)
   - Implement re-ranking (cross-encoder or simple scoring)
   - Build prompt template for GPT-4
   - Implement response generation with citations
   - Add Opik tracing integration
   - Handle edge cases (no results, API errors)
   - Containerize and deploy

2. **API Gateway**
   - Create FastAPI gateway service
   - Set up request routing
   - Implement Redis caching
   - Add rate limiting (slowapi)
   - Add CORS middleware
   - Implement health check endpoints
   - Containerize and deploy

**Deliverables:**
- ✅ Working RAG query API (`/api/search`)
- ✅ Response time < 5 seconds for typical queries
- ✅ Opik traces for all LLM calls
- ✅ API documentation (FastAPI auto-docs)

---

### Phase 3: Trend Analysis (Week 5)

**Goal:** Detect and rank emerging research trends

**Tasks:**
1. **Trend Analysis Service**
   - Extract keywords from paper abstracts (TF-IDF, KeyBERT)
   - Compute keyword frequency over time windows (30/90/180 days)
   - Implement trend growth calculation (acceleration metric)
   - Cluster papers by topic (HDBSCAN or K-means on embeddings)
   - Store trend data in Cosmos DB (trends container)
   - Schedule periodic execution (daily via Azure Function or cron)
   - Containerize and deploy

2. **Trend API Endpoints**
   - Add `/api/trends` endpoint to API Gateway
   - Support query params: `?window=30&limit=10`
   - Return trends sorted by growth rate
   - Include representative papers for each trend

**Deliverables:**
- ✅ Automated trend detection (runs daily)
- ✅ Trend API endpoint with historical data
- ✅ Trend metrics: growth rate, paper count, keywords

---

### Phase 4: Frontend Development (Week 6-7)

**Goal:** Build user-friendly Streamlit interface

**Tasks:**
1. **Core Search Interface**
   - Search bar with placeholder examples
   - Submit button + loading spinner
   - Display generated answer with markdown formatting
   - Display cited papers as cards (title, authors, abstract snippet, link)
   - Show citation links (arXiv, Semantic Scholar)

2. **Advanced Filters**
   - Date range picker (last 30/90/180 days or custom)
   - Venue multi-select (NeurIPS, ICML, arXiv categories)
   - Citation count slider (min citations)
   - Author search box

3. **Trend Visualizations**
   - "Trending Topics" tab
   - Line chart: keyword frequency over time (Plotly)
   - Bar chart: top 10 trending keywords
   - Interactive: click keyword → show related papers

4. **Paper Details & Comparison**
   - Paper detail modal (full abstract, all authors, citations)
   - "Compare" checkbox on paper cards
   - Side-by-side comparison table for selected papers

5. **Export Features**
   - Export to BibTeX button
   - Export to markdown button
   - Download citations as .bib or .md file

6. **Query History**
   - Sidebar with last 10 queries
   - Click to re-run previous query
   - Store in browser session state

7. **Deployment**
   - Containerize Streamlit app
   - Deploy to Azure Container Apps
   - Configure custom domain (optional)

**Deliverables:**
- ✅ Fully functional Streamlit UI
- ✅ Responsive design (works on desktop and tablet)
- ✅ All core features implemented
- ✅ Public URL for demo

---

### Phase 5: Observability & Evaluation (Week 8)

**Goal:** Comprehensive monitoring and quality evaluation

**Tasks:**
1. **Opik Integration**
   - Trace all LLM calls (embeddings + generation)
   - Log query, context, response, tokens, cost
   - Create Opik project and experiments
   - Implement evaluation metrics:
     - Retrieval relevance (is retrieved context relevant?)
     - Answer accuracy (does answer match retrieved papers?)
     - Citation quality (are citations correct and complete?)
   - Create evaluation dataset (10-20 test queries with ground truth)
   - Run periodic evaluations

2. **Azure Monitor Setup**
   - Configure Application Insights for all services
   - Create custom metrics (query latency, cache hit rate)
   - Set up log queries for error tracking
   - Create dashboards:
     - System health (service status, response times)
     - Usage metrics (queries per day, popular trends)
     - Cost tracking (OpenAI API spend)
   - Configure alerts (service down, high error rate, high latency)

3. **Performance Optimization**
   - Identify bottlenecks from traces
   - Optimize embedding generation (batch processing)
   - Tune Qdrant search parameters (HNSW config)
   - Optimize caching strategy
   - Load test with locust (100 concurrent users)

**Deliverables:**
- ✅ Opik dashboard with evaluation metrics
- ✅ Azure Monitor dashboard
- ✅ Alert rules configured
- ✅ Performance optimizations applied
- ✅ Load test results and report

---

### Phase 6: Scale Up & Polish (Week 9-10)

**Goal:** Ingest full dataset and final improvements

**Tasks:**
1. **Scale Ingestion**
   - Ingest ~1,000 papers from last 6 months
   - Monitor processing pipeline performance
   - Ensure no duplicates or data quality issues

2. **User Experience Polish**
   - Add onboarding tour (first-time user guide)
   - Improve error messages
   - Add example queries
   - Optimize load times
   - Add keyboard shortcuts (Enter to search)

3. **Documentation**
   - Write README with architecture diagram
   - Create API documentation
   - Write deployment guide
   - Create demo video
   - Write blog post about learnings

4. **Testing**
   - Write unit tests for critical functions
   - Write integration tests for APIs
   - Manual QA testing
   - Test edge cases

**Deliverables:**
- ✅ 1,000+ papers ingested and searchable
- ✅ Polished, production-ready UI
- ✅ Complete documentation
- ✅ Test coverage > 70%
- ✅ Demo video and blog post

---

## 7. Data Model

### 7.1 Qdrant Vector Store

**Collection:** `papers`

**Vector Configuration:**
- Dimension: 1536 (OpenAI text-embedding-3-small)
- Distance: Cosine
- Indexed: HNSW

**Payload Schema:**
```json
{
  "paper_id": "2301.12345",
  "title": "Attention Is All You Need",
  "authors": ["Ashish Vaswani", "Noam Shazeer"],
  "abstract": "The dominant sequence transduction models...",
  "published_date": "2023-01-15",
  "arxiv_url": "https://arxiv.org/abs/2301.12345",
  "semantic_scholar_id": "abc123",
  "venue": "NeurIPS 2017",
  "citation_count": 50000,
  "categories": ["cs.LG", "cs.CL"]
}
```

### 7.2 Cosmos DB Collections

#### Collection: `papers`
**Partition Key:** `/paper_id`

```json
{
  "id": "2301.12345",
  "paper_id": "2301.12345",
  "title": "Attention Is All You Need",
  "authors": [
    {"name": "Ashish Vaswani", "affiliation": "Google Brain"}
  ],
  "abstract": "Full abstract text...",
  "published_date": "2023-01-15T00:00:00Z",
  "arxiv_url": "https://arxiv.org/abs/2301.12345",
  "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
  "semantic_scholar_id": "abc123",
  "semantic_scholar_url": "https://...",
  "venue": "NeurIPS 2017",
  "citation_count": 50000,
  "citations_per_month": 416.67,
  "categories": ["cs.LG", "cs.CL"],
  "keywords": ["attention", "transformers", "neural networks"],
  "ingested_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

#### Collection: `trends`
**Partition Key:** `/window`

```json
{
  "id": "trend_30_transformers_2024-01-20",
  "window": "30",
  "keyword": "transformers",
  "paper_count": 127,
  "growth_rate": 0.45,
  "trend_score": 8.7,
  "representative_papers": ["2301.12345", "2302.54321"],
  "computed_at": "2024-01-20T12:00:00Z",
  "time_series": [
    {"date": "2024-01-01", "count": 80},
    {"date": "2024-01-15", "count": 127}
  ]
}
```

#### Collection: `query_cache`
**Partition Key:** `/query_hash`
**TTL:** 3600 seconds (1 hour)

```json
{
  "id": "abc123def456",
  "query_hash": "abc123def456",
  "query": "What are the latest trends in vision transformers?",
  "filters": {"window": 30, "min_citations": 10},
  "response": "Recent trends in vision transformers...",
  "cited_papers": ["2301.12345", "2302.54321"],
  "created_at": "2024-01-20T14:30:00Z",
  "ttl": 3600
}
```

---

## 8. API Specifications

### 8.1 RAG Query API

**Endpoint:** `POST /api/search`

**Request:**
```json
{
  "query": "What are the latest breakthroughs in large language models?",
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "min_citations": 10,
    "venues": ["NeurIPS", "ICML"],
    "categories": ["cs.CL", "cs.LG"]
  },
  "top_k": 10,
  "include_trends": true
}
```

**Response:**
```json
{
  "query": "What are the latest breakthroughs in large language models?",
  "answer": "Recent breakthroughs in large language models include...",
  "sources": [
    {
      "paper_id": "2301.12345",
      "title": "GPT-4 Technical Report",
      "authors": ["OpenAI"],
      "abstract": "We report the development of GPT-4...",
      "published_date": "2023-03-15",
      "citation_count": 1200,
      "arxiv_url": "https://arxiv.org/abs/2303.08774",
      "relevance_score": 0.95
    }
  ],
  "related_trends": [
    {
      "keyword": "large language models",
      "growth_rate": 0.67,
      "paper_count": 234
    }
  ],
  "metadata": {
    "retrieval_time_ms": 450,
    "generation_time_ms": 2300,
    "total_time_ms": 2750,
    "tokens_used": 3500,
    "cost_usd": 0.0175
  }
}
```

### 8.2 Trends API

**Endpoint:** `GET /api/trends?window=30&limit=10`

**Response:**
```json
{
  "window": 30,
  "trends": [
    {
      "keyword": "vision transformers",
      "paper_count": 156,
      "growth_rate": 0.82,
      "trend_score": 9.2,
      "representative_papers": [
        {
          "paper_id": "2301.12345",
          "title": "Scalable Vision Transformers...",
          "citation_count": 450
        }
      ],
      "time_series": [
        {"date": "2024-01-01", "count": 85},
        {"date": "2024-01-30", "count": 156}
      ]
    }
  ],
  "computed_at": "2024-01-30T12:00:00Z"
}
```

### 8.3 Paper Details API

**Endpoint:** `GET /api/papers/{paper_id}`

**Response:**
```json
{
  "paper_id": "2301.12345",
  "title": "Attention Is All You Need",
  "authors": [
    {"name": "Ashish Vaswani", "affiliation": "Google Brain"}
  ],
  "abstract": "Full abstract...",
  "published_date": "2017-06-12",
  "arxiv_url": "https://arxiv.org/abs/1706.03762",
  "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
  "citation_count": 50000,
  "citations_per_month": 520,
  "venue": "NeurIPS 2017",
  "categories": ["cs.CL", "cs.LG"],
  "keywords": ["attention", "transformers"],
  "related_papers": [
    {"paper_id": "2302.54321", "similarity": 0.89}
  ]
}
```

---

## 9. Observability Strategy

### 9.1 Opik Integration

**What to Track:**
- Every LLM API call (embeddings + generation)
- Query input and output
- Retrieved context (which papers, relevance scores)
- Response generation (prompt, response, tokens, cost)
- Latency breakdown (retrieval, generation, total)

**Evaluation Metrics:**
1. **Retrieval Quality:**
   - Are retrieved papers relevant to the query?
   - Metric: Average relevance score (human-labeled test set)

2. **Answer Quality:**
   - Does the answer accurately reflect the retrieved papers?
   - Are citations correct?
   - Metric: Human evaluation (1-5 scale)

3. **Latency:**
   - Target: < 5 seconds end-to-end
   - Track p50, p95, p99 latencies

4. **Cost:**
   - Track cost per query
   - Monitor daily/monthly spend

**Implementation:**
```python
import opik

# Initialize Opik client
opik_client = opik.Opik(api_key=os.getenv("OPIK_API_KEY"))

# Trace a query
with opik_client.trace("rag_query") as trace:
    # Retrieval step
    with trace.span("retrieval") as span:
        results = qdrant_client.search(query_embedding, limit=10)
        span.log({"retrieved_count": len(results)})

    # Generation step
    with trace.span("generation") as span:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[...]
        )
        span.log({
            "tokens": response.usage.total_tokens,
            "cost": calculate_cost(response.usage)
        })

    trace.log({"query": query, "answer": response.choices[0].message.content})
```

### 9.2 Azure Monitor

**Metrics to Track:**
- Request rate (requests/min)
- Error rate (errors/min)
- Response time (p50, p95, p99)
- Service health (up/down)
- Cache hit rate
- Queue depth (Service Bus)

**Dashboards:**
1. **System Health Dashboard**
   - Service status indicators
   - Error rate chart
   - Request rate chart

2. **Performance Dashboard**
   - Latency percentiles
   - Cache hit rate
   - API response times

3. **Cost Dashboard**
   - OpenAI API spend
   - Azure service costs
   - Cost per query

**Alerts:**
- Service down (any container app)
- Error rate > 5%
- Latency p95 > 10 seconds
- Daily OpenAI spend > $10

---

## 10. Deployment Guide

### 10.1 Prerequisites
- Azure subscription
- Azure CLI installed
- Docker installed
- OpenAI API key
- Python 3.11+

### 10.2 Deployment Steps

#### Step 1: Azure Resource Provisioning
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-ai-research-trends --location eastus

# Create Azure Container Registry
az acr create --resource-group rg-ai-research-trends \
  --name airesearchtrendsacr --sku Basic

# Create Cosmos DB account
az cosmosdb create --name ai-research-cosmos \
  --resource-group rg-ai-research-trends \
  --kind GlobalDocumentDB

# Create Cosmos DB database and containers
az cosmosdb sql database create \
  --account-name ai-research-cosmos \
  --resource-group rg-ai-research-trends \
  --name ai-research-db

az cosmosdb sql container create \
  --account-name ai-research-cosmos \
  --database-name ai-research-db \
  --name papers \
  --partition-key-path "/paper_id"

# Create Service Bus namespace and queue
az servicebus namespace create \
  --name ai-research-servicebus \
  --resource-group rg-ai-research-trends

az servicebus queue create \
  --namespace-name ai-research-servicebus \
  --name paper-ingestion-queue \
  --resource-group rg-ai-research-trends

# Create Key Vault
az keyvault create --name ai-research-kv \
  --resource-group rg-ai-research-trends --location eastus

# Store OpenAI API key
az keyvault secret set --vault-name ai-research-kv \
  --name openai-api-key --value "YOUR_OPENAI_KEY"
```

#### Step 2: Build and Push Container Images
```bash
# Login to ACR
az acr login --name airesearchtrendsacr

# Build and push services
docker build -t airesearchtrendsacr.azurecr.io/qdrant:latest ./services/qdrant
docker push airesearchtrendsacr.azurecr.io/qdrant:latest

docker build -t airesearchtrendsacr.azurecr.io/processing:latest ./services/processing
docker push airesearchtrendsacr.azurecr.io/processing:latest

# Repeat for all services...
```

#### Step 3: Deploy Container Apps
```bash
# Create Container Apps environment
az containerapp env create \
  --name ai-research-env \
  --resource-group rg-ai-research-trends \
  --location eastus

# Deploy Qdrant
az containerapp create \
  --name qdrant \
  --resource-group rg-ai-research-trends \
  --environment ai-research-env \
  --image airesearchtrendsacr.azurecr.io/qdrant:latest \
  --target-port 6333 \
  --ingress internal \
  --min-replicas 1 --max-replicas 1

# Deploy other services...
```

#### Step 4: Deploy Azure Functions
```bash
# Create Function App
az functionapp create \
  --resource-group rg-ai-research-trends \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name ai-research-functions \
  --storage-account aireserachstorage

# Deploy function code
cd services/ingestion-function
func azure functionapp publish ai-research-functions
```

### 10.3 Environment Variables

**Processing Service:**
```env
OPENAI_API_KEY=<from Key Vault>
QDRANT_URL=http://qdrant:6333
COSMOS_ENDPOINT=<Cosmos DB endpoint>
COSMOS_KEY=<from Key Vault>
SERVICEBUS_CONNECTION_STRING=<from Key Vault>
```

**RAG Query Service:**
```env
OPENAI_API_KEY=<from Key Vault>
QDRANT_URL=http://qdrant:6333
COSMOS_ENDPOINT=<Cosmos DB endpoint>
OPIK_API_KEY=<Opik API key>
```

---

## 11. Cost Estimation (MVP)

| Service | Usage | Monthly Cost (USD) |
|---------|-------|-------------------|
| **OpenAI API** | | |
| - Embeddings (text-embedding-3-small) | 1K papers × 500 tokens × $0.02/1M | $0.01 |
| - GPT-4 (generation) | 100 queries × 4K tokens × $30/1M | $12.00 |
| **Azure Container Apps** | | |
| - 6 containers × $0.000024/vCPU-second | 6 × 0.5 vCPU × 730 hrs | $15.00 |
| **Azure Cosmos DB** | 1K papers, 100 RU/s | ~$5.00 |
| **Azure Service Bus** | 1M operations | ~$0.05 |
| **Azure Functions** | 10 executions/week | Free tier |
| **Azure Cache for Redis** | Basic 250 MB | ~$15.00 |
| **Azure Blob Storage** | 1 GB | ~$0.02 |
| **Azure Monitor** | Basic logs | ~$2.00 |
| **Opik** | Free tier | $0.00 |
| **TOTAL** | | **~$50/month** |

**Note:** Costs will increase with usage. At 1,000 queries/month with 10K papers, expect ~$100-150/month.

---

## 12. Testing Strategy

### 12.1 Unit Tests
- Test data parsers (arXiv, Semantic Scholar)
- Test embedding generation
- Test vector search logic
- Test prompt formatting
- Test citation extraction

### 12.2 Integration Tests
- Test end-to-end ingestion flow
- Test query flow (API → Qdrant → OpenAI → Response)
- Test trend computation
- Test caching behavior

### 12.3 Load Tests
- Use `locust` to simulate 100 concurrent users
- Target: 95% of requests < 5 seconds
- Test cache performance

### 12.4 Evaluation Tests
- Create test dataset (20 queries with expected answers)
- Measure retrieval precision@5
- Measure answer relevance (human eval)
- Run weekly regression tests

---

## 13. Future Enhancements (Post-MVP)

### 13.1 Features
- **Email Alerts:** Weekly digest of new trends
- **Saved Searches:** Bookmark queries and get updates
- **Paper Recommendations:** "Papers similar to X"
- **Multi-language Support:** Support non-English papers
- **Author Profiles:** Aggregate author stats and trends
- **Citation Graph:** Visualize paper citation networks
- **PDF Full-text Search:** Extract and search full paper text
- **Collaborative Features:** Share searches with teams

### 13.2 Technical Improvements
- **Agentic RAG:** Use LLM to plan multi-step retrieval
- **Fine-tuned Embeddings:** Train custom embeddings on research papers
- **Graph RAG:** Use knowledge graphs for better context
- **Multi-modal:** Support paper figures and diagrams
- **Real-time Ingestion:** Stream papers as they're published
- **Auto-scaling:** Scale containers based on load
- **A/B Testing:** Test different retrieval/generation strategies

### 13.3 Monetization (Optional)
- Free tier: 10 queries/day
- Pro tier ($20/month): Unlimited queries, advanced filters, alerts
- Enterprise tier ($200/month): API access, custom data sources

---

## 14. Learning Outcomes

By completing this project, you will learn:

**Backend Engineering:**
- ✅ Microservices architecture design
- ✅ Asynchronous processing with message queues
- ✅ RESTful API design with FastAPI
- ✅ Container orchestration with Docker

**Cloud Engineering (Azure):**
- ✅ Azure Container Apps (managed Kubernetes)
- ✅ Azure Functions (serverless)
- ✅ Azure Cosmos DB (NoSQL database)
- ✅ Azure Service Bus (messaging)
- ✅ Azure Key Vault (secrets management)
- ✅ Infrastructure as Code (Azure CLI)

**AI/ML Engineering:**
- ✅ RAG architecture (retrieval + generation)
- ✅ Vector embeddings and similarity search
- ✅ Hybrid search (semantic + keyword)
- ✅ LLM prompt engineering
- ✅ Evaluation and observability (Opik)

**Data Engineering:**
- ✅ ETL pipelines (ingestion → processing → storage)
- ✅ Data modeling for NoSQL and vector databases
- ✅ Batch and stream processing

**DevOps:**
- ✅ CI/CD with GitHub Actions (optional)
- ✅ Container registry and deployment
- ✅ Monitoring and alerting
- ✅ Cost optimization

---

## 15. Success Criteria

**Technical:**
- ✅ System ingests 1,000+ AI research papers
- ✅ Query response time < 5 seconds (p95)
- ✅ Retrieval precision@5 > 80%
- ✅ Answer quality score > 4/5 (human eval)
- ✅ System uptime > 99% (measured over 1 month)
- ✅ All services containerized and deployed to Azure
- ✅ Opik traces for 100% of queries
- ✅ Monthly cost < $100

**User Experience:**
- ✅ Users can ask natural language questions and get accurate answers
- ✅ Users can discover emerging trends with visualizations
- ✅ Users can filter and export papers
- ✅ UI is responsive and intuitive

**Learning:**
- ✅ You can explain the RAG architecture to others
- ✅ You can troubleshoot and debug Azure services
- ✅ You can evaluate and improve LLM-powered systems
- ✅ You have a portfolio-worthy project to showcase

---

## 16. Next Steps

1. **Review this plan** and ask questions
2. **Set up Azure account** and create resource group
3. **Start with Phase 1** (Foundation & Data Ingestion)
4. **Build iteratively** - test each component before moving to next
5. **Document learnings** as you go (keep a dev journal)
6. **Share progress** (blog, LinkedIn, GitHub)

**Recommended Timeline:** 10 weeks (part-time, ~10-15 hrs/week)

---

## 17. Resources

**Azure Documentation:**
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Functions Python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/)

**RAG & LLM:**
- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

**Observability:**
- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Azure Monitor Best Practices](https://learn.microsoft.com/en-us/azure/azure-monitor/)

**Data Sources:**
- [arXiv API](https://arxiv.org/help/api/)
- [Semantic Scholar API](https://www.semanticscholar.org/product/api)

---

## 18. Project Structure

```
ai-research-trends-rag/
├── README.md
├── claude.md                    # This file
├── .gitignore
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── api-specs.md
│   └── deployment-guide.md
│
├── services/
│   ├── ingestion-function/      # Azure Function
│   │   ├── function_app.py
│   │   ├── requirements.txt
│   │   └── host.json
│   │
│   ├── processing-service/      # Container App
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── embeddings.py
│   │       ├── storage.py
│   │       └── utils.py
│   │
│   ├── trend-analysis-service/  # Container App
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── app/
│   │       ├── trend_detection.py
│   │       └── clustering.py
│   │
│   ├── rag-query-service/       # Container App
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── app/
│   │       ├── retrieval.py
│   │       ├── generation.py
│   │       └── prompts.py
│   │
│   ├── api-gateway/             # Container App
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── app/
│   │       ├── routes.py
│   │       └── middleware.py
│   │
│   └── frontend/                # Streamlit Container App
│       ├── Dockerfile
│       ├── app.py
│       ├── requirements.txt
│       └── components/
│           ├── search.py
│           ├── trends.py
│           └── filters.py
│
├── infra/                       # Infrastructure as Code
│   ├── azure-resources.sh       # Azure CLI commands
│   └── docker-compose.yml       # Local development
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── load/
│       └── locustfile.py
│
├── notebooks/                   # Jupyter notebooks for experimentation
│   ├── data_exploration.ipynb
│   └── trend_analysis_prototype.ipynb
│
└── scripts/
    ├── deploy.sh
    └── seed_data.py             # Script to ingest initial papers
```

---

## Conclusion

This is a comprehensive, production-grade RAG system that will teach you end-to-end ML engineering on Azure. The architecture is scalable, observable, and follows best practices for microservices.

The MVP is achievable in 10 weeks part-time, and you'll have a portfolio project that demonstrates:
- Cloud-native architecture
- AI/ML engineering
- Full-stack development
- DevOps practices

**Let's build this!** Start with Phase 1 and iterate from there. Feel free to adjust the plan based on your learning pace and interests.
