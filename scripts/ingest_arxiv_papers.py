"""
Script to ingest papers from arXiv API and send them to the processing service.

This is a standalone script for local development. For production, this logic
will be moved to an Azure Function with Service Bus integration.
"""
import os
import sys
import logging
import time
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PROCESSING_SERVICE_URL = os.getenv("PROCESSING_SERVICE_URL", "http://localhost:8000")
ARXIV_API_BASE = "http://export.arxiv.org/api/query"


class ArxivIngestion:
    """Handles ingestion of papers from arXiv."""

    def __init__(self, processing_service_url: str):
        """Initialize the ingestion handler."""
        self.processing_service_url = processing_service_url

    def build_arxiv_query(
        self,
        categories: List[str],
        max_results: int = 100,
        days_back: int = 7
    ) -> str:
        """
        Build arXiv API query URL.

        Args:
            categories: List of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
            max_results: Maximum number of results to fetch
            days_back: Number of days to look back

        Returns:
            Query URL
        """
        # Build category query (OR condition)
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])

        # Build date filter
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        date_to = datetime.now().strftime("%Y%m%d")

        # Combine query
        # Note: arXiv API date filtering is limited, so we'll filter after fetching
        query = f"search_query=({cat_query})&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

        url = f"{ARXIV_API_BASE}?{query}"
        logger.info(f"Built arXiv query URL: {url}")
        return url

    def fetch_arxiv_papers(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CL"],
        max_results: int = 100,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch papers from arXiv API.

        Args:
            categories: List of arXiv categories to search
            max_results: Maximum number of results
            days_back: Number of days to look back

        Returns:
            List of paper dictionaries
        """
        logger.info(f"Fetching papers from arXiv: categories={categories}, max_results={max_results}")

        url = self.build_arxiv_query(categories, max_results, days_back)

        try:
            # Fetch from arXiv
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.content)

            papers = []
            for entry in feed.entries:
                try:
                    # Extract arXiv ID from entry.id
                    # Format: http://arxiv.org/abs/2301.12345v1
                    arxiv_id = entry.id.split('/abs/')[-1]
                    if 'v' in arxiv_id:
                        arxiv_id = arxiv_id.split('v')[0]  # Remove version

                    # Extract categories
                    entry_categories = []
                    if hasattr(entry, 'tags'):
                        entry_categories = [tag['term'] for tag in entry.tags]

                    # Extract authors
                    authors = []
                    if hasattr(entry, 'authors'):
                        authors = [author['name'] for author in entry.authors]

                    # Parse published date
                    published_date = entry.published
                    if hasattr(entry, 'published_parsed'):
                        pub_time = time.mktime(entry.published_parsed)
                        published_date = datetime.fromtimestamp(pub_time).isoformat()

                    # Build paper object
                    paper = {
                        "paper_id": arxiv_id,
                        "title": entry.title,
                        "authors": authors,
                        "abstract": entry.summary.replace('\n', ' '),
                        "published_date": published_date,
                        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                        "categories": entry_categories,
                        # Semantic Scholar data will be added later
                        "semantic_scholar_id": None,
                        "semantic_scholar_url": None,
                        "venue": None,
                        "citation_count": 0
                    }

                    papers.append(paper)
                    logger.info(f"Parsed paper: {arxiv_id} - {entry.title[:50]}...")

                except Exception as e:
                    logger.error(f"Error parsing entry: {str(e)}")
                    continue

            logger.info(f"Successfully fetched {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from arXiv: {str(e)}")
            raise

    def send_to_processing_service(self, paper: Dict[str, Any]) -> bool:
        """
        Send a paper to the processing service.

        Args:
            paper: Paper dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.processing_service_url}/process"
            response = requests.post(url, json=paper, timeout=60)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Processed paper {paper['paper_id']}: {result['status']}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending paper {paper['paper_id']} to processing service: {str(e)}")
            return False

    def ingest_papers(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CL"],
        max_results: int = 100,
        days_back: int = 7
    ):
        """
        Main ingestion workflow: fetch papers and send to processing service.

        Args:
            categories: arXiv categories to search
            max_results: Maximum number of results
            days_back: Number of days to look back
        """
        logger.info("Starting paper ingestion workflow...")

        # Fetch papers from arXiv
        papers = self.fetch_arxiv_papers(categories, max_results, days_back)

        if not papers:
            logger.warning("No papers fetched from arXiv")
            return

        # Send papers to processing service
        success_count = 0
        failure_count = 0

        for i, paper in enumerate(papers, 1):
            logger.info(f"Processing paper {i}/{len(papers)}: {paper['paper_id']}")

            if self.send_to_processing_service(paper):
                success_count += 1
            else:
                failure_count += 1

            # Add small delay to avoid overwhelming the processing service
            time.sleep(0.5)

        logger.info(
            f"Ingestion complete. Success: {success_count}, "
            f"Failed: {failure_count}, Total: {len(papers)}"
        )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest papers from arXiv")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["cs.AI", "cs.LG", "cs.CL"],
        help="arXiv categories to search"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum number of results to fetch"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=7,
        help="Number of days to look back"
    )
    parser.add_argument(
        "--processing-url",
        default=PROCESSING_SERVICE_URL,
        help="Processing service URL"
    )

    args = parser.parse_args()

    # Create ingestion handler
    ingestion = ArxivIngestion(processing_service_url=args.processing_url)

    # Run ingestion
    try:
        ingestion.ingest_papers(
            categories=args.categories,
            max_results=args.max_results,
            days_back=args.days_back
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
