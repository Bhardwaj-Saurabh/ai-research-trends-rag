"""
AI Research Trends Discovery - Streamlit Frontend
Main application file.
"""
import streamlit as st
from datetime import datetime, timedelta
import random

from config import (
    APP_TITLE,
    APP_ICON,
    APP_DESCRIPTION,
    EXAMPLE_QUERIES,
    DEFAULT_TOP_K,
    RAG_SERVICE_URL,
    PROCESSING_SERVICE_URL
)
from utils import (
    query_rag_service,
    check_service_health,
    get_service_stats,
    format_paper_card,
    export_to_bibtex,
    export_to_markdown,
    initialize_session_state,
    add_to_query_history
)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .paper-card {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.markdown("---")

    # Service Status
    st.markdown("### 🔧 Service Status")

    rag_health = check_service_health(RAG_SERVICE_URL)
    proc_health = check_service_health(PROCESSING_SERVICE_URL)

    if rag_health.get('status') == 'healthy':
        st.success("✓ RAG Service: Online")
    else:
        st.error("✗ RAG Service: Offline")

    if proc_health.get('status') == 'healthy':
        st.success("✓ Processing Service: Online")
    else:
        st.error("✗ Processing Service: Offline")

    st.markdown("---")

    # Collection Stats
    st.markdown("### 📊 Collection Stats")
    stats = get_service_stats(RAG_SERVICE_URL)
    if 'error' not in stats:
        st.metric("Papers Indexed", stats.get('points_count', 0))
    else:
        st.warning("Stats unavailable")

    st.markdown("---")

    # Query History
    st.markdown("### 📜 Query History")
    if st.session_state.query_history:
        for i, item in enumerate(st.session_state.query_history[:5]):
            with st.expander(f"Query {i+1}", expanded=False):
                st.markdown(f"**Q:** {item['query'][:50]}...")
                st.caption(f"{item['num_sources']} sources")
    else:
        st.info("No queries yet")

    st.markdown("---")

    # Advanced Options
    with st.expander("⚙️ Advanced Options"):
        top_k = st.slider(
            "Number of papers to retrieve",
            min_value=1,
            max_value=10,
            value=DEFAULT_TOP_K,
            help="More papers = more context but slower"
        )
        st.session_state.top_k = top_k

    # About
    with st.expander("ℹ️ About"):
        st.markdown("""
        This platform uses Retrieval-Augmented Generation (RAG) to help you discover and understand AI research trends.

        **Features:**
        - Natural language search
        - GPT-4 powered answers
        - Citation-backed responses
        - Real-time paper ingestion

        **Data Sources:**
        - arXiv (cs.AI, cs.LG, cs.CL)
        - Semantic Scholar
        """)

# Main content
st.markdown(f'<p class="main-header">{APP_ICON} {APP_TITLE}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{APP_DESCRIPTION}</p>', unsafe_allow_html=True)

# Check if services are available
if rag_health.get('status') != 'healthy':
    st.error(f"""
    ⚠️ RAG Service is not available. Please ensure the service is running at {RAG_SERVICE_URL}

    To start the service:
    ```bash
    cd services/rag-query-service
    uvicorn main:app --reload --port 8001
    ```
    """)
    st.stop()

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search", "📈 Statistics", "💡 Help"])

with tab1:
    # Search Interface
    st.markdown("### Ask a Research Question")

    # Example queries
    with st.expander("💡 Example Questions", expanded=False):
        cols = st.columns(2)
        for i, example in enumerate(EXAMPLE_QUERIES[:6]):
            col = cols[i % 2]
            with col:
                if st.button(example, key=f"example_{i}", use_container_width=True):
                    st.session_state.example_query = example

    # Query input
    default_query = st.session_state.get('example_query', '')
    query = st.text_area(
        "Enter your question:",
        value=default_query,
        height=100,
        placeholder="e.g., What are the latest developments in transformer models?",
        help="Ask any question about AI research papers in the database"
    )

    # Clear the example query after use
    if 'example_query' in st.session_state:
        del st.session_state.example_query

    # Search button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)

    if clear_button:
        st.session_state.current_results = None
        st.rerun()

    # Process query
    if search_button and query.strip():
        with st.spinner("🤔 Thinking... (this may take 5-10 seconds)"):
            top_k = st.session_state.get('top_k', DEFAULT_TOP_K)
            result = query_rag_service(query, top_k=top_k)

            if result:
                st.session_state.current_results = result
                add_to_query_history(query, result)
                st.rerun()

    # Display results
    if st.session_state.current_results:
        result = st.session_state.current_results

        st.markdown("---")
        st.markdown("### 💬 Answer")

        # Display the answer in a nice card
        st.info(result.get('answer', 'No answer generated'))

        # Metadata
        metadata = result.get('metadata', {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Processing Time", f"{metadata.get('processing_time_ms', 0)}ms")
        with col2:
            st.metric("Tokens Used", metadata.get('tokens_used', 0))
        with col3:
            st.metric("Papers Retrieved", metadata.get('papers_retrieved', 0))
        with col4:
            st.metric("Model", metadata.get('model', 'N/A'))

        st.markdown("---")

        # Display sources
        sources = result.get('sources', [])
        if sources:
            st.markdown(f"### 📚 Source Papers ({len(sources)})")

            # Export buttons
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                bibtex = export_to_bibtex(sources)
                st.download_button(
                    "📥 Export BibTeX",
                    data=bibtex,
                    file_name="papers.bib",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                markdown = export_to_markdown(sources)
                st.download_button(
                    "📥 Export Markdown",
                    data=markdown,
                    file_name="papers.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            st.markdown("---")

            # Display papers
            for i, paper in enumerate(sources, 1):
                format_paper_card(paper, i)
        else:
            st.warning("No source papers found for this query.")

with tab2:
    st.markdown("### 📊 System Statistics")

    # Get stats from both services
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### RAG Query Service")
        rag_stats = get_service_stats(RAG_SERVICE_URL)
        if 'error' not in rag_stats:
            st.metric("Collection", rag_stats.get('collection', 'N/A'))
            st.metric("Papers Indexed", rag_stats.get('points_count', 0))
            st.metric("Vectors Stored", rag_stats.get('vectors_count', 0))
        else:
            st.error("Could not retrieve stats")

    with col2:
        st.markdown("#### Processing Service")
        proc_stats = get_service_stats(PROCESSING_SERVICE_URL)
        if 'error' not in proc_stats:
            st.metric("Collection", proc_stats.get('collection', 'N/A'))
            stats_info = proc_stats.get('statistics', {})
            st.json(stats_info)
        else:
            st.error("Could not retrieve stats")

    st.markdown("---")

    # Query history stats
    st.markdown("### 📜 Query History")
    if st.session_state.query_history:
        st.dataframe(
            [{
                'Query': item['query'][:50] + '...',
                'Sources': item['num_sources'],
                'Timestamp': item['timestamp']
            } for item in st.session_state.query_history],
            use_container_width=True
        )
    else:
        st.info("No queries in history")

with tab3:
    st.markdown("### 💡 How to Use")

    st.markdown("""
    #### 🔍 Searching for Papers

    1. **Enter your question** in the search box
    2. Click **Search** or press Enter
    3. Wait for the AI to generate an answer (5-10 seconds)
    4. Review the answer and source papers

    #### 💡 Tips for Better Results

    - **Be specific**: Instead of "transformers", try "How do vision transformers differ from CNNs?"
    - **Ask about trends**: "What are emerging trends in multimodal learning?"
    - **Request comparisons**: "Compare BERT and GPT architectures"
    - **Adjust retrieval count**: Use the slider in the sidebar to retrieve more/fewer papers

    #### 📥 Exporting Papers

    - Click **Export BibTeX** to download citations in BibTeX format
    - Click **Export Markdown** to save papers as a formatted document
    - Use these exports for your research papers or reference management tools

    #### ⚙️ Advanced Options

    - **Number of papers**: Control how many papers are retrieved (more = more context)
    - **Query History**: Access your previous searches in the sidebar

    #### 🔧 Troubleshooting

    **"RAG Service: Offline"**
    - Make sure the RAG service is running: `cd services/rag-query-service && uvicorn main:app --reload --port 8001`

    **"No relevant papers found"**
    - Try rephrasing your query
    - Make sure papers have been ingested: `python scripts/ingest_arxiv_papers.py`

    **Query takes too long**
    - Reduce the number of papers to retrieve
    - Check your internet connection (OpenAI API calls)
    """)

    st.markdown("---")

    st.markdown("### 🛠️ System Requirements")
    st.code("""
# Services that need to be running:
1. Qdrant (vector database): docker-compose up -d qdrant
2. Processing Service: uvicorn main:app --reload (port 8000)
3. RAG Query Service: uvicorn main:app --reload --port 8001
4. Frontend (this app): streamlit run app.py

# Optional:
- Cosmos DB (for production)
- Azure Service Bus (for production)
    """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔬 AI Research Trends Discovery")
with col2:
    st.caption("Powered by OpenAI GPT-4 & Qdrant")
with col3:
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
