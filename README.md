# AI Research Trends RAG 🔬

A production-grade Retrieval-Augmented Generation (RAG) platform for discovering and analyzing AI research trends. Built with microservices architecture, deployed on Azure, and powered by OpenAI GPT-4.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

- **Natural Language Search**: Ask questions about AI research in plain English
- **GPT-4 Powered Answers**: Get comprehensive, citation-backed responses
- **Semantic Search**: Vector-based similarity search using embeddings
- **Real-time Ingestion**: Continuously ingest papers from arXiv and Semantic Scholar
- **Beautiful UI**: Clean Streamlit interface with visualizations
- **Export Capabilities**: Download citations in BibTeX or Markdown format
- **Microservices Architecture**: Scalable, containerized services
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                  Streamlit Frontend (Port 8501)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Query Service                         │
│              FastAPI (Port 8001)                             │
│  • Query Understanding  • Retrieval  • Re-ranking            │
│  • GPT-4 Generation    • Citation Management                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Vector Database Layer                       │
│               Qdrant (Port 6333)                             │
│         1536-dim embeddings, HNSW index                      │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Processing Service                          │
│              FastAPI (Port 8000)                             │
│  • Embedding Generation  • Duplicate Detection               │
│  • Vector Storage       • Metadata Management                │
└────────────────────────▲────────────────────────────────────┘
                         │
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Data Ingestion Layer                        │
│            arXiv API + Semantic Scholar API                  │
│        Python Script (Future: Azure Function)                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ~2GB disk space

### Option 1: Interactive Demo (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-research-trends-rag

# Run the interactive demo
./scripts/run_local_demo.sh

# Follow the prompts to:
# 1. Set up your OpenAI API key
# 2. Start all services
# 3. Ingest sample papers
# 4. Open the web interface
```

### Option 2: Manual Setup

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# 2. Start Qdrant
docker-compose up -d qdrant

# 3. Start Processing Service (Terminal 1)
cd services/processing-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Ingest papers (Terminal 2)
pip install -r services/ingestion-function/requirements.txt
python scripts/ingest_arxiv_papers.py --max-results 10

# 5. Start RAG Service (Terminal 3)
cd services/rag-query-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# 6. Start Frontend (Terminal 4)
cd services/frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# 7. Open browser to http://localhost:8501
```

## 📖 Documentation

- **[Quick Start Guide](docs/quick-start.md)** - Get up and running in 5 minutes
- **[Local Testing Guide](docs/local-testing-guide.md)** - Comprehensive testing instructions
- **[Architecture Overview](docs/architecture.md)** - System design and components
- **[Deployment Guide](docs/deployment-guide.md)** - Deploy to Azure
- **[Frontend Guide](services/frontend/README.md)** - Streamlit UI documentation
- **[Implementation Plan](claude.md)** - Full development roadmap

## 🎯 Usage Examples

### Search for Papers

```bash
# Via API
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest developments in transformer models?",
    "top_k": 5
  }'

# Via Web UI
# Open http://localhost:8501 and type your question
```

### Ingest Papers

```bash
# Ingest 50 papers from last 7 days
python scripts/ingest_arxiv_papers.py \
  --max-results 50 \
  --days-back 7 \
  --categories cs.AI cs.LG cs.CL
```

## 🧪 Testing

```bash
# Run automated tests
python scripts/test_services.py

# Check service health
curl http://localhost:8000/health  # Processing Service
curl http://localhost:8001/health  # RAG Query Service

# View collection stats
curl http://localhost:8000/stats
```

## 📊 Current Status

### ✅ Completed (Phase 1)

- [x] Project structure and configuration
- [x] Processing Service (embeddings + storage)
- [x] RAG Query Service (retrieval + generation)
- [x] Streamlit Frontend
- [x] arXiv ingestion script
- [x] Local development environment
- [x] Documentation and guides
- [x] Testing utilities

### ⏳ In Progress

- [ ] API Gateway (caching + rate limiting)
- [ ] Trend Analysis Service
- [ ] Azure Function for scheduled ingestion
- [ ] Opik integration for observability
- [ ] Advanced filters and search

### 📅 Planned (Phase 2)

- [ ] Azure deployment (Container Apps)
- [ ] Cosmos DB integration
- [ ] Service Bus integration
- [ ] Citation graph visualization
- [ ] Email alerts for trends
- [ ] Multi-language support

See [PROGRESS.md](PROGRESS.md) for detailed status.

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | OpenAI GPT-4 | Answer generation |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search |
| **Vector DB** | Qdrant | Fast similarity search |
| **API Framework** | FastAPI | REST APIs |
| **Frontend** | Streamlit | Web interface |
| **Container** | Docker | Containerization |
| **Cloud** | Azure | Production deployment |
| **Monitoring** | Opik (planned) | LLM observability |

## 💰 Cost Estimation

**Local Development**: ~$1-2/day
- OpenAI API (embeddings + GPT-4): $1-2
- Everything else is free (local Docker)

**Production (MVP)**: ~$50-100/month
- Azure Container Apps: ~$15-30
- Azure Cosmos DB: ~$5-10
- OpenAI API: ~$20-50
- Other Azure services: ~$10-20

See [claude.md](claude.md) for detailed cost breakdown.

## 📁 Project Structure

```
ai-research-trends-rag/
├── docs/                      # Documentation
│   ├── architecture.md
│   ├── deployment-guide.md
│   ├── quick-start.md
│   └── local-testing-guide.md
├── services/                  # Microservices
│   ├── processing-service/    # Embeddings & storage
│   ├── rag-query-service/     # RAG query handler
│   ├── frontend/              # Streamlit UI
│   ├── api-gateway/           # (Coming soon)
│   └── trend-analysis-service/ # (Coming soon)
├── scripts/                   # Utility scripts
│   ├── ingest_arxiv_papers.py
│   ├── test_services.py
│   └── run_local_demo.sh
├── infra/                     # Infrastructure as Code
│   └── azure-resources.sh
├── docker-compose.yml         # Local development
├── .env.example               # Environment template
├── claude.md                  # Implementation plan
├── PROGRESS.md                # Development progress
└── README.md                  # This file
```

## 🤝 Contributing

This is a learning project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

**Services won't start?**
- Check [Local Testing Guide](docs/local-testing-guide.md) troubleshooting section
- Verify all prerequisites are installed
- Check port availability (6333, 8000, 8001, 8501)

**No papers found in searches?**
- Verify papers were ingested: `curl http://localhost:8000/stats`
- Re-run ingestion: `python scripts/ingest_arxiv_papers.py --max-results 10`
- Check Qdrant dashboard: http://localhost:6333/dashboard

**OpenAI errors?**
- Verify API key in `.env` file
- Check OpenAI account has credits
- Review rate limits on OpenAI dashboard

See full troubleshooting guide in [docs/local-testing-guide.md](docs/local-testing-guide.md).

## 📚 Learning Resources

This project demonstrates:
- **RAG Architecture**: Retrieval-Augmented Generation patterns
- **Vector Search**: Semantic similarity with embeddings
- **Microservices**: Building distributed systems
- **FastAPI**: Modern Python web frameworks
- **Azure Cloud**: Container Apps, Cosmos DB, Service Bus
- **LLM Integration**: Working with GPT-4 and embeddings
- **Full-Stack Development**: Backend APIs + Frontend UI

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embedding models
- Qdrant for the vector database
- arXiv for providing free access to research papers
- Semantic Scholar for citation data
- Streamlit for the UI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-research-trends-rag/issues)
- **Questions**: Check the [Help tab](http://localhost:8501) in the web interface
- **Documentation**: See [docs/](docs/) directory

---

**Built with ❤️ for learning end-to-end ML systems**

*Last updated: 2024-12-23*
