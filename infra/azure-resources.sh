#!/bin/bash

# Azure AI Research Trends RAG - Infrastructure Setup Script
# This script creates all required Azure resources

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="rg-ai-research-trends"
LOCATION="eastus"
ACR_NAME="airesearchtrendsacr"
COSMOS_ACCOUNT="ai-research-cosmos"
COSMOS_DB="ai-research-db"
SERVICEBUS_NAMESPACE="ai-research-servicebus"
KEYVAULT_NAME="ai-research-kv"
STORAGE_ACCOUNT="airesearchstorage"
CONTAINER_ENV="ai-research-env"

echo "======================================"
echo "Azure AI Research Trends RAG Setup"
echo "======================================"
echo ""

# Check if logged in to Azure
echo "Checking Azure login status..."
az account show > /dev/null 2>&1 || {
    echo "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

echo "Logged in successfully!"
echo ""

# Create Resource Group
echo "Creating resource group: $RESOURCE_GROUP..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo ""

# Create Azure Container Registry
echo "Creating Azure Container Registry: $ACR_NAME..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output table

echo ""

# Create Cosmos DB Account
echo "Creating Cosmos DB account: $COSMOS_ACCOUNT..."
az cosmosdb create \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --kind GlobalDocumentDB \
    --locations regionName=$LOCATION failoverPriority=0 \
    --default-consistency-level Session \
    --output table

echo ""

# Create Cosmos DB Database
echo "Creating Cosmos DB database: $COSMOS_DB..."
az cosmosdb sql database create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --name $COSMOS_DB \
    --output table

echo ""

# Create Cosmos DB Containers
echo "Creating Cosmos DB containers..."

# Papers container
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --database-name $COSMOS_DB \
    --name papers \
    --partition-key-path "/paper_id" \
    --throughput 400 \
    --output table

# Trends container
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --database-name $COSMOS_DB \
    --name trends \
    --partition-key-path "/window" \
    --throughput 400 \
    --output table

# Query cache container with TTL
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --database-name $COSMOS_DB \
    --name query-cache \
    --partition-key-path "/query_hash" \
    --throughput 400 \
    --ttl 3600 \
    --output table

echo ""

# Create Service Bus Namespace
echo "Creating Service Bus namespace: $SERVICEBUS_NAMESPACE..."
az servicebus namespace create \
    --name $SERVICEBUS_NAMESPACE \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard \
    --output table

echo ""

# Create Service Bus Queues
echo "Creating Service Bus queues..."

az servicebus queue create \
    --namespace-name $SERVICEBUS_NAMESPACE \
    --name paper-ingestion-queue \
    --resource-group $RESOURCE_GROUP \
    --max-delivery-count 10 \
    --output table

az servicebus queue create \
    --namespace-name $SERVICEBUS_NAMESPACE \
    --name trend-analysis-queue \
    --resource-group $RESOURCE_GROUP \
    --max-delivery-count 10 \
    --output table

echo ""

# Create Key Vault
echo "Creating Key Vault: $KEYVAULT_NAME..."
az keyvault create \
    --name $KEYVAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo ""

# Create Storage Account
echo "Creating Storage Account: $STORAGE_ACCOUNT..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --output table

echo ""

# Create Blob Containers
echo "Creating blob containers..."
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query '[0].value' -o tsv)

az storage container create \
    --name paper-pdfs \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

az storage container create \
    --name exports \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

echo ""

# Create Container Apps Environment
echo "Creating Container Apps Environment: $CONTAINER_ENV..."
az containerapp env create \
    --name $CONTAINER_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo ""

# Get connection strings and endpoints
echo "======================================"
echo "Resource Creation Complete!"
echo "======================================"
echo ""
echo "Important connection strings and endpoints:"
echo ""

echo "1. Azure Container Registry:"
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
echo "   Login Server: $ACR_LOGIN_SERVER"
echo ""

echo "2. Cosmos DB:"
COSMOS_ENDPOINT=$(az cosmosdb show --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP --query documentEndpoint -o tsv)
COSMOS_KEY=$(az cosmosdb keys list --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP --query primaryMasterKey -o tsv)
echo "   Endpoint: $COSMOS_ENDPOINT"
echo "   Primary Key: $COSMOS_KEY"
echo ""

echo "3. Service Bus:"
SERVICEBUS_CONN=$(az servicebus namespace authorization-rule keys list \
    --namespace-name $SERVICEBUS_NAMESPACE \
    --name RootManageSharedAccessKey \
    --resource-group $RESOURCE_GROUP \
    --query primaryConnectionString -o tsv)
echo "   Connection String: $SERVICEBUS_CONN"
echo ""

echo "4. Storage Account:"
STORAGE_CONN=$(az storage account show-connection-string \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)
echo "   Connection String: $STORAGE_CONN"
echo ""

# Store secrets in Key Vault
echo "Storing connection strings in Key Vault..."
az keyvault secret set --vault-name $KEYVAULT_NAME --name cosmos-key --value "$COSMOS_KEY" > /dev/null
az keyvault secret set --vault-name $KEYVAULT_NAME --name servicebus-connection --value "$SERVICEBUS_CONN" > /dev/null
az keyvault secret set --vault-name $KEYVAULT_NAME --name storage-connection --value "$STORAGE_CONN" > /dev/null

echo ""
echo "Next steps:"
echo "1. Store your OpenAI API key in Key Vault:"
echo "   az keyvault secret set --vault-name $KEYVAULT_NAME --name openai-api-key --value \"YOUR_KEY\""
echo ""
echo "2. Update your .env file with the above values"
echo ""
echo "3. Login to ACR:"
echo "   az acr login --name $ACR_NAME"
echo ""
echo "Setup complete! 🎉"
