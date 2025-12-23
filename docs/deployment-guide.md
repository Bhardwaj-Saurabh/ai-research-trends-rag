# Deployment Guide

## Prerequisites

- Azure CLI installed (`az --version`)
- Docker installed (`docker --version`)
- Python 3.11+ installed
- OpenAI API key
- Azure subscription with sufficient credits

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd ai-research-trends-rag

# Create .env file from example
cp .env.example .env

# Edit .env and add your OpenAI API key
```

### 2. Provision Azure Resources

```bash
# Login to Azure
az login

# Run the infrastructure setup script
cd infra
./azure-resources.sh

# This will create:
# - Resource Group
# - Azure Container Registry
# - Cosmos DB (with containers)
# - Service Bus (with queues)
# - Key Vault
# - Blob Storage
# - Container Apps Environment
```

### 3. Store Secrets

```bash
# Store your OpenAI API key in Key Vault
az keyvault secret set \
  --vault-name ai-research-kv \
  --name openai-api-key \
  --value "your_openai_api_key"

# Store Opik API key
az keyvault secret set \
  --vault-name ai-research-kv \
  --name opik-api-key \
  --value "your_opik_api_key"
```

### 4. Build and Push Container Images

```bash
# Login to ACR
az acr login --name airesearchtrendsacr

# Build and push each service
cd services/processing-service
docker build -t airesearchtrendsacr.azurecr.io/processing:latest .
docker push airesearchtrendsacr.azurecr.io/processing:latest

cd ../rag-query-service
docker build -t airesearchtrendsacr.azurecr.io/rag-query:latest .
docker push airesearchtrendsacr.azurecr.io/rag-query:latest

cd ../api-gateway
docker build -t airesearchtrendsacr.azurecr.io/api-gateway:latest .
docker push airesearchtrendsacr.azurecr.io/api-gateway:latest

cd ../frontend
docker build -t airesearchtrendsacr.azurecr.io/frontend:latest .
docker push airesearchtrendsacr.azurecr.io/frontend:latest
```

### 5. Deploy Container Apps

See deployment scripts in `infra/deploy-containers.sh`

### 6. Deploy Azure Functions

```bash
cd services/ingestion-function
func azure functionapp publish ai-research-functions
```

## Local Development

### Run with Docker Compose

```bash
# Create .env file with local settings
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Services

- Frontend: http://localhost:8501
- API Gateway: http://localhost:8000
- RAG Query Service: http://localhost:8001
- Qdrant UI: http://localhost:6333/dashboard

## Monitoring

### Azure Monitor
- Navigate to Azure Portal → Monitor → Application Insights
- View logs, metrics, and dashboards

### Opik
- Visit Opik dashboard
- View LLM traces and evaluation metrics

## Troubleshooting

### Container Apps Not Starting
- Check logs: `az containerapp logs show --name <app-name> --resource-group rg-ai-research-trends`
- Verify environment variables
- Check Key Vault access

### High Latency
- Check Opik traces for bottlenecks
- Verify Redis cache is working
- Optimize Qdrant search parameters

### Out of Memory
- Increase container memory allocation
- Optimize batch sizes in processing service
