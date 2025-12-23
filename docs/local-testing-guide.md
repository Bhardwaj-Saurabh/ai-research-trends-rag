# Local Testing Guide

Complete guide to test the AI Research Trends RAG system locally.

## Prerequisites Checklist

- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] OpenAI API key ready
- [ ] ~2GB disk space available
- [ ] Ports 6333, 8000, 8001, 8501 available

## Option 1: Manual Setup (Recommended for Learning)

This approach lets you see each component working individually.

### Step 1: Environment Setup

```bash
# Navigate to project root
cd ai-research-trends-rag

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Use your favorite editor (nano, vim, code, etc.)
nano .env
```

Add this line to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 2: Start Qdrant

```bash
# Start Qdrant vector database
docker-compose up -d qdrant

# Verify it's running
curl http://localhost:6333/collections

# Visit dashboard (optional)
open http://localhost:6333/dashboard
```

### Step 3: Start Processing Service

**Terminal 1:**
```bash
cd services/processing-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test it:**
```bash
# In another terminal
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"processing-service",...}
```

### Step 4: Ingest Some Papers

**Terminal 2:**
```bash
# Install ingestion script dependencies
pip install -r services/ingestion-function/requirements.txt

# Ingest 10 papers (takes ~1-2 minutes)
python scripts/ingest_arxiv_papers.py --max-results 10

# You should see output like:
# INFO - Fetching papers from arXiv...
# INFO - Parsed paper: 2401.12345 - ...
# INFO - Processed paper 2401.12345: success
```

**Verify papers were stored:**
```bash
curl http://localhost:8000/stats

# You should see points_count > 0
```

### Step 5: Start RAG Query Service

**Terminal 3:**
```bash
cd services/rag-query-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the service (note the different port!)
uvicorn main:app --reload --port 8001

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8001
```

**Test it:**
```bash
# In another terminal
curl http://localhost:8001/health

# Try a query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are transformer models?",
    "top_k": 3
  }'

# You should get a JSON response with an answer and sources!
```

### Step 6: Start Streamlit Frontend

**Terminal 4:**
```bash
cd services/frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py

# Browser should open automatically to http://localhost:8501
```

### Step 7: Use the Application!

1. **Check Service Status**: Green checkmarks in sidebar = all good ✅
2. **Try Example Query**: Click an example question or type your own
3. **Wait for Answer**: Takes 5-10 seconds (calling OpenAI)
4. **Review Results**: See the answer and source papers
5. **Export**: Download citations as BibTeX or Markdown

---

## Option 2: Docker Compose (Coming Soon)

For now, the API Gateway service is not yet built, so full Docker Compose deployment will come later. Use Option 1 (Manual Setup) for now.

---

## Verification Checklist

Use this checklist to verify everything is working:

### Qdrant
- [ ] Dashboard accessible at http://localhost:6333/dashboard
- [ ] Collection "papers" exists
- [ ] Points count > 0

### Processing Service (Port 8000)
- [ ] Health check returns "healthy"
- [ ] Stats show papers indexed
- [ ] Can process a new paper via `/process` endpoint

### RAG Query Service (Port 8001)
- [ ] Health check returns "healthy"
- [ ] Can query papers via `/query` endpoint
- [ ] Returns answer with sources

### Frontend (Port 8501)
- [ ] Page loads in browser
- [ ] Service status shows green checkmarks
- [ ] Can submit a query
- [ ] Receives answer and source papers
- [ ] Can export as BibTeX or Markdown

---

## Test Queries to Try

### Basic Questions
```
What are transformer models?
Explain vision transformers
How do large language models work?
```

### Trend Questions
```
What are the latest developments in diffusion models?
What are emerging trends in reinforcement learning?
How is self-supervised learning being used?
```

### Comparison Questions
```
Compare BERT and GPT architectures
What are the differences between CNNs and vision transformers?
Compare supervised and self-supervised learning approaches
```

### Specific Topics
```
How are transformers used in computer vision?
What are the challenges in training large language models?
How do attention mechanisms work in neural networks?
```

---

## Troubleshooting

### "Connection refused" errors

**Problem**: Can't connect to a service

**Solutions**:
1. Check the service is running: `ps aux | grep uvicorn`
2. Verify the port is correct (8000 for processing, 8001 for RAG)
3. Check for port conflicts: `lsof -i :8000`
4. Restart the service

### "OpenAI API key not found"

**Problem**: Services can't access OpenAI API

**Solutions**:
1. Verify `.env` file exists in project root
2. Check `OPENAI_API_KEY=sk-...` is in `.env`
3. Restart the services after adding the key
4. Check environment is loaded: `echo $OPENAI_API_KEY`

### "No papers found"

**Problem**: Queries return no results

**Solutions**:
1. Check papers were ingested: `curl http://localhost:8000/stats`
2. Re-run ingestion: `python scripts/ingest_arxiv_papers.py --max-results 10`
3. Check Qdrant dashboard: http://localhost:6333/dashboard
4. Verify collection "papers" exists with points

### "Rate limit exceeded"

**Problem**: OpenAI API rate limit hit

**Solutions**:
1. Wait 60 seconds and try again
2. Check your OpenAI usage: https://platform.openai.com/usage
3. Reduce `--max-results` when ingesting
4. Add delays between requests

### Services crash or won't start

**Problem**: Python errors or import issues

**Solutions**:
1. Verify Python version: `python --version` (should be 3.11+)
2. Recreate virtual environment:
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Check for missing dependencies
4. Review error messages in logs

### Qdrant not accessible

**Problem**: Can't connect to Qdrant

**Solutions**:
1. Check Docker is running: `docker ps`
2. Start Qdrant: `docker-compose up -d qdrant`
3. Check logs: `docker-compose logs qdrant`
4. Verify port 6333 is available: `lsof -i :6333`

---

## Performance Tips

### Faster Response Times
- Reduce `top_k` in queries (fewer papers = faster)
- Use shorter, more specific queries
- Ensure good internet connection for OpenAI API

### Better Results
- Ingest more papers (50-100)
- Use higher `top_k` for complex questions
- Be specific in your queries

### Cost Optimization
- Start with small batches (10 papers)
- Test with short queries first
- Monitor OpenAI usage dashboard

---

## Running Automated Tests

```bash
# Run the test suite
python scripts/test_services.py

# This will test:
# - Processing service health and endpoints
# - RAG query service health and endpoints
# - End-to-end query flow
```

---

## Cleaning Up

### Stop Services
```bash
# Stop all terminals running Python services (Ctrl+C)

# Stop Qdrant
docker-compose down

# Or stop and remove data
docker-compose down -v  # WARNING: Deletes all papers!
```

### Clean Virtual Environments
```bash
# From each service directory
rm -rf venv
```

### Full Reset
```bash
# Stop everything
docker-compose down -v

# Remove all virtual environments
find . -name "venv" -type d -exec rm -rf {} +

# Start fresh from Step 1
```

---

## Next Steps

Once you have everything working locally:

1. **Ingest More Papers**: Try 50-100 papers for better results
2. **Experiment with Queries**: Test different question types
3. **Review the Code**: Understand how RAG works
4. **Build Trend Analysis**: Next feature to implement
5. **Deploy to Azure**: Production deployment

---

## Getting Help

**Check logs**:
```bash
# Processing Service
# Look at Terminal 1 where uvicorn is running

# RAG Query Service
# Look at Terminal 3 where uvicorn is running

# Qdrant
docker-compose logs qdrant

# Streamlit
# Look at Terminal 4 where streamlit is running
```

**Common Log Locations**:
- Service logs: Terminal output
- Docker logs: `docker-compose logs <service-name>`
- Application logs: In service terminal windows

**Resources**:
- [Quick Start Guide](./quick-start.md)
- [Architecture Overview](./architecture.md)
- [Deployment Guide](./deployment-guide.md)
- [Frontend README](../services/frontend/README.md)
