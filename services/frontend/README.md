# AI Research Trends - Streamlit Frontend

Beautiful, interactive web interface for discovering AI research trends.

## Features

### 🔍 Natural Language Search
- Ask questions in plain English
- Get AI-generated answers backed by research papers
- View source papers with relevance scores

### 📚 Source Paper Display
- Clean, card-based layout
- Paper metadata (authors, citations, venue, date)
- Expandable abstracts
- Direct links to arXiv

### 📊 System Statistics
- Real-time service health monitoring
- Collection statistics
- Query history tracking

### 📥 Export Capabilities
- Export citations as BibTeX
- Export papers as Markdown
- Perfect for research papers and reference managers

### 💡 User-Friendly Features
- Example queries to get started
- Query history in sidebar
- Adjustable retrieval parameters
- Service status indicators
- Helpful tooltips and guides

## Quick Start

### 1. Install Dependencies

```bash
cd services/frontend
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure these services are running:
- Qdrant: `docker-compose up -d qdrant`
- Processing Service: Running on port 8000
- RAG Query Service: Running on port 8001

### 3. Run the App

```bash
streamlit run app.py
```

The app will open automatically at http://localhost:8501

## Environment Variables

Create a `.env` file (optional):

```env
RAG_SERVICE_URL=http://localhost:8001
PROCESSING_SERVICE_URL=http://localhost:8000
```

## Usage

### Basic Search

1. Enter your research question in the search box
2. Click "Search" or press Enter
3. Wait for the AI to generate an answer (5-10 seconds)
4. Review the answer and source papers

### Example Questions

- "What are the latest developments in transformer models?"
- "Explain vision transformers and their applications"
- "What are emerging trends in large language models?"
- "How is reinforcement learning being used in robotics?"

### Advanced Options

Access via the sidebar:
- **Number of papers**: Control retrieval count (1-10)
- **Query History**: View and re-run previous searches

### Exporting Results

- **BibTeX**: For LaTeX/reference managers
- **Markdown**: For documentation/notes

## Troubleshooting

### "RAG Service: Offline"

The RAG service is not running. Start it:

```bash
cd services/rag-query-service
uvicorn main:app --reload --port 8001
```

### "No relevant papers found"

- Ensure papers have been ingested
- Try rephrasing your query
- Check the collection stats in the Statistics tab

### Slow Response Times

- Reduce the number of papers to retrieve
- Check your internet connection (OpenAI API)
- Verify all services are healthy

## Docker Deployment

Build and run with Docker:

```bash
docker build -t frontend:latest .
docker run -p 8501:8501 \
  -e RAG_SERVICE_URL=http://rag-service:8000 \
  frontend:latest
```

Or use Docker Compose:

```bash
docker-compose up frontend
```

## Development

### Project Structure

```
frontend/
├── app.py              # Main Streamlit application
├── config.py           # Configuration and constants
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
└── .streamlit/
    └── config.toml     # Streamlit theme and settings
```

### Adding New Features

1. **New Tab**: Add to the `st.tabs()` list in `app.py`
2. **New Utility**: Add to `utils.py`
3. **Configuration**: Update `config.py`

### Customizing the Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4F46E5"  # Main accent color
backgroundColor = "#FFFFFF"  # Background
secondaryBackgroundColor = "#F3F4F6"  # Sidebar/cards
textColor = "#1F2937"  # Text color
```

## Features in Detail

### 🔍 Search Tab

- **Query Input**: Natural language question box
- **Example Queries**: Click to try sample questions
- **Answer Display**: AI-generated response in a nice card
- **Metadata**: Processing time, tokens used, model info
- **Source Papers**: Expandable cards with full metadata
- **Export Buttons**: Download citations in multiple formats

### 📊 Statistics Tab

- **Service Stats**: Collection size, papers indexed
- **Query History Table**: All previous searches
- **Service Health**: Real-time status monitoring

### 💡 Help Tab

- **How to Use**: Step-by-step guide
- **Tips**: Best practices for queries
- **Troubleshooting**: Common issues and solutions
- **System Requirements**: What needs to be running

## Tips for Best Results

1. **Be Specific**: "How do vision transformers differ from CNNs?" is better than just "transformers"

2. **Ask About Trends**: "What are emerging trends in X?" works well

3. **Request Comparisons**: "Compare A and B" leverages multiple papers

4. **Adjust Retrieval**: More papers = more context but slower response

5. **Use Query History**: Easily re-run previous successful queries

## API Integration

The frontend communicates with two backend services:

### RAG Query Service (Port 8001)

```python
POST /query
{
  "query": "Your question here",
  "top_k": 5,
  "include_sources": true
}
```

### Processing Service (Port 8000)

```python
GET /stats  # Get collection statistics
GET /health # Check service health
```

## Next Steps

- **Add Filters**: Date range, venue, citation count
- **Trend Visualization**: Charts showing research trends over time
- **Paper Comparison**: Side-by-side comparison of multiple papers
- **User Authentication**: Save queries and preferences
- **Advanced Search**: Boolean operators, field-specific search

## Support

For issues or questions:
1. Check the Help tab in the application
2. Review the troubleshooting section above
3. Ensure all services are running and healthy
