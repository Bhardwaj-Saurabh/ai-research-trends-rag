# Quick Start Guide

Get the AI Research Trends RAG system running locally in minutes!

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ~500MB disk space for Docker images

## Setup Steps

### 1. Clone and Configure

```bash
# Navigate to project directory
cd ai-research-trends-rag

# Run setup script
./scripts/setup_local.sh

# This will:
# - Create .env file from template
# - Prompt you to add your OpenAI API key
# - Start Qdrant vector database
```

### 2. Add Your OpenAI API Key

Edit the `.env` file:

```bash
# Open .env in your editor
nano .env  # or vim, code, etc.

# Replace this line:
OPENAI_API_KEY=your_openai_api_key_here

# With your actual key:
OPENAI_API_KEY=sk-...your-key-here...
```

### 3. Start the Processing Service

```bash
# Navigate to processing service
cd services/processing-service

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --reload
```

The service will start on `http://localhost:8000`

### 4. Test the Service

Open another terminal and test the health endpoint:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "processing-service",
  "qdrant_connected": true,
  "cosmos_connected": true,
  "timestamp": "2024-01-20T10:30:00.123456"
}
```

### 5. Ingest Papers from arXiv

```bash
# Install script dependencies
pip install -r services/ingestion-function/requirements.txt

# Ingest 10 recent AI papers
python scripts/ingest_arxiv_papers.py --max-results 10

# Watch the logs - you should see papers being processed!
```

### 6. Verify Papers are Stored

```bash
# Check collection stats
curl http://localhost:8000/stats
```

Or visit the Qdrant dashboard: http://localhost:6333/dashboard

## What's Next?

Now that you have papers in the system, you can:

1. **Build the RAG Query Service** to ask questions about papers
2. **Build the Frontend** to interact with the system
3. **Add more papers** by running the ingestion script with different parameters

## Troubleshooting

### "Connection refused" when starting processing service

- Make sure Qdrant is running: `docker-compose ps`
- If not, start it: `docker-compose up -d qdrant`

### "OpenAI API key not found"

- Check your `.env` file has `OPENAI_API_KEY=sk-...`
- Make sure you're running from the project root directory
- The processing service needs to be able to find the `.env` file

### "Rate limit exceeded" from OpenAI

- You've hit OpenAI API rate limits
- Wait a minute and try again
- Reduce `--max-results` when ingesting papers

### Papers not appearing in Qdrant

- Check processing service logs for errors
- Verify the ingestion script completed successfully
- Check Qdrant dashboard: http://localhost:6333/dashboard

## Useful Commands

```bash
# View running containers
docker-compose ps

# View Qdrant logs
docker-compose logs -f qdrant

# Stop all services
docker-compose down

# Reset everything (WARNING: deletes all data)
docker-compose down -v
rm -rf venv
```

## API Documentation

Once the processing service is running, visit:
- **OpenAPI Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps

- [Build RAG Query Service](./rag-query-service.md)
- [Build Frontend](./frontend.md)
- [Deploy to Azure](./deployment-guide.md)
