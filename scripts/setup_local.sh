#!/bin/bash

# Local Development Setup Script

set -e

echo "======================================"
echo "AI Research Trends RAG - Local Setup"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter once you've added your OpenAI API key to .env..."
else
    echo "✓ .env file already exists"
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo ""
    echo "⚠️  WARNING: OpenAI API key not set in .env file"
    echo "   Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

echo ""
echo "Starting Docker containers..."
docker-compose up -d qdrant

echo ""
echo "Waiting for Qdrant to start..."
sleep 5

echo ""
echo "✓ Local development environment ready!"
echo ""
echo "Next steps:"
echo "1. Start the processing service:"
echo "   cd services/processing-service"
echo "   python -m venv venv"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   pip install -r requirements.txt"
echo "   uvicorn main:app --reload"
echo ""
echo "2. In another terminal, ingest some papers:"
echo "   python scripts/ingest_arxiv_papers.py --max-results 10"
echo ""
echo "3. Check Qdrant dashboard at:"
echo "   http://localhost:6333/dashboard"
echo ""
echo "Happy coding! 🚀"
