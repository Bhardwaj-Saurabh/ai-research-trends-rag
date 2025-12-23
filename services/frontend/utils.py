"""Utility functions for the Streamlit frontend."""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st
from config import RAG_SERVICE_URL, PROCESSING_SERVICE_URL, QUERY_TIMEOUT


def query_rag_service(
    query: str,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a query to the RAG service.

    Args:
        query: User's research question
        top_k: Number of papers to retrieve
        filters: Optional search filters

    Returns:
        Response from RAG service
    """
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "include_sources": True
        }

        if filters:
            payload["filters"] = filters

        response = requests.post(
            f"{RAG_SERVICE_URL}/query",
            json=payload,
            timeout=QUERY_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        st.error("Request timed out. The service might be processing a complex query.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to RAG service at {RAG_SERVICE_URL}. Is it running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error querying RAG service: {str(e)}")
        return None


def check_service_health(service_url: str) -> Dict[str, Any]:
    """
    Check if a service is healthy.

    Args:
        service_url: Base URL of the service

    Returns:
        Health status dictionary
    """
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def get_service_stats(service_url: str) -> Dict[str, Any]:
    """
    Get statistics from a service.

    Args:
        service_url: Base URL of the service

    Returns:
        Statistics dictionary
    """
    try:
        response = requests.get(f"{service_url}/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def format_paper_card(paper: Dict[str, Any], index: int) -> None:
    """
    Display a paper as a card in Streamlit.

    Args:
        paper: Paper data
        index: Paper index for display
    """
    with st.container():
        # Header with title and relevance score
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {index}. {paper.get('title', 'Untitled')}")
        with col2:
            score = paper.get('relevance_score', 0)
            st.metric("Relevance", f"{score:.2f}")

        # Authors
        authors = paper.get('authors', [])
        if authors:
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += f" et al. (+{len(authors) - 3})"
            st.markdown(f"**Authors:** {author_str}")

        # Metadata row
        col1, col2, col3 = st.columns(3)
        with col1:
            pub_date = paper.get('published_date', 'Unknown')
            if pub_date and pub_date != 'Unknown':
                try:
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    pub_date = date_obj.strftime("%b %d, %Y")
                except:
                    pass
            st.markdown(f"📅 **Published:** {pub_date}")

        with col2:
            citations = paper.get('citation_count', 0)
            st.markdown(f"📚 **Citations:** {citations}")

        with col3:
            venue = paper.get('venue', 'N/A')
            if venue and venue != 'N/A':
                st.markdown(f"🏛️ **Venue:** {venue}")

        # Abstract
        abstract = paper.get('abstract', 'No abstract available.')
        with st.expander("📄 View Abstract"):
            st.write(abstract)

        # Links
        arxiv_url = paper.get('arxiv_url', '')
        if arxiv_url:
            st.markdown(f"[🔗 View on arXiv]({arxiv_url})")

        st.divider()


def export_to_bibtex(papers: List[Dict[str, Any]]) -> str:
    """
    Convert papers to BibTeX format.

    Args:
        papers: List of papers

    Returns:
        BibTeX string
    """
    bibtex_entries = []

    for paper in papers:
        paper_id = paper.get('paper_id', 'unknown')
        title = paper.get('title', 'Untitled')
        authors = paper.get('authors', [])
        year = "Unknown"

        # Extract year from published_date
        pub_date = paper.get('published_date', '')
        if pub_date:
            try:
                date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                year = str(date_obj.year)
            except:
                pass

        # Format authors for BibTeX
        author_str = " and ".join(authors) if authors else "Unknown"

        # Create BibTeX entry
        entry = f"""@article{{{paper_id},
  title = {{{title}}},
  author = {{{author_str}}},
  year = {{{year}}},
  journal = {{arXiv preprint}},
  url = {{{paper.get('arxiv_url', '')}}}
}}"""
        bibtex_entries.append(entry)

    return "\n\n".join(bibtex_entries)


def export_to_markdown(papers: List[Dict[str, Any]]) -> str:
    """
    Convert papers to Markdown format.

    Args:
        papers: List of papers

    Returns:
        Markdown string
    """
    md_lines = ["# Research Papers\n"]

    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'Untitled')
        authors = paper.get('authors', [])
        author_str = ", ".join(authors) if authors else "Unknown"
        pub_date = paper.get('published_date', 'Unknown')
        arxiv_url = paper.get('arxiv_url', '')
        abstract = paper.get('abstract', 'No abstract available.')

        md_lines.append(f"## {i}. {title}\n")
        md_lines.append(f"**Authors:** {author_str}\n")
        md_lines.append(f"**Published:** {pub_date}\n")
        if arxiv_url:
            md_lines.append(f"**URL:** {arxiv_url}\n")
        md_lines.append(f"\n**Abstract:**\n{abstract}\n")
        md_lines.append("\n---\n")

    return "\n".join(md_lines)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    if 'current_results' not in st.session_state:
        st.session_state.current_results = None

    if 'selected_papers' not in st.session_state:
        st.session_state.selected_papers = []


def add_to_query_history(query: str, result: Dict[str, Any]):
    """Add a query to the history."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    st.session_state.query_history.insert(0, {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'num_sources': len(result.get('sources', [])),
        'answer_preview': result.get('answer', '')[:100] + '...'
    })

    # Keep only last 10 queries
    st.session_state.query_history = st.session_state.query_history[:10]
