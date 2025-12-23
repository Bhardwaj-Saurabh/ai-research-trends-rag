#!/bin/bash

# AI Research Trends RAG - Local Demo Script
# This script helps you run a quick demo of the system

set -e

clear

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Research Trends RAG - Local Demo                      ║"
echo "║   Interactive setup and testing script                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

PREREQS_OK=true

if command_exists docker; then
    echo "✓ Docker installed"
else
    echo "✗ Docker not found - Please install Docker Desktop"
    PREREQS_OK=false
fi

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python installed (version $PYTHON_VERSION)"
else
    echo "✗ Python 3 not found - Please install Python 3.11+"
    PREREQS_OK=false
fi

if [ "$PREREQS_OK" = false ]; then
    echo ""
    echo "❌ Prerequisites not met. Please install missing software."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚙️  Setting up environment..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your OpenAI API key!"
    echo ""
    echo "Please edit .env and add your key:"
    echo "  OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "Get an API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

# Verify OpenAI key is set
if grep -q "your_openai_api_key_here" .env; then
    echo ""
    echo "❌ OpenAI API key not set in .env file"
    echo "   Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Qdrant is already running
if docker ps | grep -q qdrant; then
    echo "✓ Qdrant is already running"
else
    echo "🚀 Starting Qdrant vector database..."
    docker-compose up -d qdrant
    echo "✓ Qdrant started"
    echo "   Waiting for Qdrant to be ready..."
    sleep 5
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 What would you like to do?"
echo ""
echo "1) Full demo (recommended for first time)"
echo "   - Start all services"
echo "   - Ingest 10 sample papers"
echo "   - Open frontend in browser"
echo ""
echo "2) Just start the frontend (if you already have data)"
echo "   - Assumes services are running"
echo "   - Opens Streamlit UI"
echo ""
echo "3) Just ingest papers (if services are running)"
echo "   - Fetch papers from arXiv"
echo "   - Process and store them"
echo ""
echo "4) Run tests"
echo "   - Test all services"
echo ""
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "           FULL DEMO - This will take a few minutes"
        echo "═══════════════════════════════════════════════════════════"
        echo ""

        echo "📦 Installing dependencies for Processing Service..."
        cd services/processing-service
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        echo "✓ Processing Service dependencies installed"
        echo ""

        echo "🚀 Starting Processing Service in background..."
        uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/processing.log 2>&1 &
        PROC_PID=$!
        sleep 3
        echo "✓ Processing Service started (PID: $PROC_PID)"
        cd ../..
        echo ""

        echo "📦 Installing dependencies for RAG Query Service..."
        cd services/rag-query-service
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        echo "✓ RAG Query Service dependencies installed"
        echo ""

        echo "🚀 Starting RAG Query Service in background..."
        uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/rag.log 2>&1 &
        RAG_PID=$!
        sleep 3
        echo "✓ RAG Query Service started (PID: $RAG_PID)"
        cd ../..
        echo ""

        echo "📚 Ingesting 10 sample papers from arXiv..."
        echo "   (This will take 1-2 minutes)"
        pip install -q -r services/ingestion-function/requirements.txt
        python3 scripts/ingest_arxiv_papers.py --max-results 10
        echo ""

        echo "📦 Installing dependencies for Frontend..."
        cd services/frontend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        echo "✓ Frontend dependencies installed"
        echo ""

        echo "🎨 Starting Streamlit Frontend..."
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║  Your browser should open automatically!                   ║"
        echo "║  If not, visit: http://localhost:8501                      ║"
        echo "║                                                             ║"
        echo "║  Background services running:                              ║"
        echo "║  - Processing Service: http://localhost:8000               ║"
        echo "║  - RAG Query Service: http://localhost:8001                ║"
        echo "║  - Qdrant Dashboard: http://localhost:6333/dashboard       ║"
        echo "║                                                             ║"
        echo "║  Press Ctrl+C to stop Streamlit                            ║"
        echo "║  Services will continue running in background              ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""

        streamlit run app.py
        ;;

    2)
        echo ""
        echo "🎨 Starting Streamlit Frontend..."
        cd services/frontend
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        streamlit run app.py
        ;;

    3)
        echo ""
        read -p "How many papers to ingest? (default: 10): " NUM_PAPERS
        NUM_PAPERS=${NUM_PAPERS:-10}

        echo ""
        echo "📚 Ingesting $NUM_PAPERS papers from arXiv..."
        pip install -q -r services/ingestion-function/requirements.txt
        python3 scripts/ingest_arxiv_papers.py --max-results $NUM_PAPERS
        echo ""
        echo "✓ Done! You can now query these papers."
        ;;

    4)
        echo ""
        echo "🧪 Running tests..."
        pip install -q requests
        python3 scripts/test_services.py
        ;;

    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;

    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
