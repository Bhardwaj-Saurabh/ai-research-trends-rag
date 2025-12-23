"""
Improved arXiv ingestion script with proper rate limiting.

This version implements proper rate limiting for both arXiv and Semantic Scholar APIs
to respect their usage policies and avoid getting blocked.
"""
import os
import sys
import logging
import time
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import our rate limiter
from rate_limiter import arxiv_rate_limiter, semantic_scholar_rate_limiter, with_retry

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
SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/v1"
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")


class ImprovedArxivIngestion:
    """Handles ingestion of papers from arXiv with proper rate limiting."""

    def __init__(self, processing_service_url: str):
        """Initialize the ingestion handler."""
        self.processing_service_url = processing_service_url
        self.semantic_scholar_api_key = SEMANTIC_SCHOLAR_API_KEY

    def build_arxiv_query(
        self,
        categories: List[str],
        max_results: int = 100,
        days_back: int = 7
    ) -> str:
        """Build arXiv API query URL."""
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"search_query=({cat_query})&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        url = f"{ARXIV_API_BASE}?{query}"
        logger.info(f"Built arXiv query URL")
        return url

    @arxiv_rate_limiter
    @with_retry(max_retries=3, backoff=2.0)
    def fetch_arxiv_papers(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CL"],
        max_results: int = 100,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch papers from arXiv API with rate limiting.

        Rate limit: 3 seconds between requests (arXiv recommendation)
        Max: 20 requests per minute
        """
        logger.info(f"Fetching papers from arXiv: categories={categories}, max_results={max_results}")
        logger.info(f"⏱️  Rate limiting enabled: 3s between requests, max 20/minute")

        url = self.build_arxiv_query(categories, max_results, days_back)

        # This function is decorated with @arxiv_rate_limiter
        # so it will automatically wait if needed
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse feed
        feed = feedparser.parse(response.content)

        papers = []
        for entry in feed.entries:
            try:
                # Extract arXiv ID
                arxiv_id = entry.id.split('/abs/')[-1]
                if 'v' in arxiv_id:
                    arxiv_id = arxiv_id.split('v')[0]

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
                    # Semantic Scholar data will be added separately
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

    @semantic_scholar_rate_limiter
    @with_retry(max_retries=3, backoff=2.0)
    def enrich_with_semantic_scholar(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Enrich paper with Semantic Scholar data.

        Rate limit (free tier): 100 requests per 5 minutes
        Rate limit (with API key): 5,000 requests per 5 minutes
        """
        try:
            # Semantic Scholar accepts arXiv IDs
            url = f"{SEMANTIC_SCHOLAR_API_BASE}/paper/arXiv:{arxiv_id}"

            headers = {}
            if self.semantic_scholar_api_key:
                headers['x-api-key'] = self.semantic_scholar_api_key
                logger.debug(f"Using Semantic Scholar API key for {arxiv_id}")

            # This function is decorated with @semantic_scholar_rate_limiter
            # so it will automatically wait if needed
            response = requests.get(url, headers=headers, timeout=10)

            # If paper not found, that's okay
            if response.status_code == 404:
                logger.debug(f"Paper {arxiv_id} not found in Semantic Scholar")
                return None

            response.raise_for_status()
            data = response.json()

            enrichment = {
                "semantic_scholar_id": data.get('paperId'),
                "semantic_scholar_url": data.get('url'),
                "venue": data.get('venue'),
                "citation_count": len(data.get('citations', [])),
            }

            logger.info(
                f"Enriched {arxiv_id}: {enrichment['citation_count']} citations, "
                f"venue: {enrichment['venue'] or 'N/A'}"
            )
            return enrichment

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit exceeded for Semantic Scholar API!")
                raise
            logger.warning(f"HTTP error enriching {arxiv_id}: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error enriching {arxiv_id} with Semantic Scholar: {str(e)}")
            return None

    @with_retry(max_retries=3, backoff=1.0)
    def send_to_processing_service(self, paper: Dict[str, Any]) -> bool:
        """Send a paper to the processing service."""
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
        days_back: int = 7,
        enrich_with_citations: bool = True
    ):
        """
        Main ingestion workflow with proper rate limiting.

        Args:
            categories: arXiv categories to search
            max_results: Maximum number of results
            days_back: Number of days to look back
            enrich_with_citations: Whether to enrich with Semantic Scholar data
        """
        logger.info("="*60)
        logger.info("Starting paper ingestion workflow with rate limiting")
        logger.info("="*60)
        logger.info(f"Categories: {categories}")
        logger.info(f"Max results: {max_results}")
        logger.info(f"Enrich with citations: {enrich_with_citations}")
        logger.info("")

        # Fetch papers from arXiv
        logger.info("Step 1: Fetching papers from arXiv...")
        papers = self.fetch_arxiv_papers(categories, max_results, days_back)

        if not papers:
            logger.warning("No papers fetched from arXiv")
            return

        logger.info(f"✓ Fetched {len(papers)} papers from arXiv")
        logger.info("")

        # Enrich with Semantic Scholar data
        if enrich_with_citations:
            logger.info("Step 2: Enriching with Semantic Scholar citation data...")
            logger.info("⏱️  Rate limiting: 100 requests per 5 minutes (free tier)")
            logger.info(f"   This will take ~{len(papers) * 3 / 60:.1f} minutes")
            logger.info("")

            enriched_count = 0
            for i, paper in enumerate(papers, 1):
                logger.info(f"Enriching paper {i}/{len(papers)}: {paper['paper_id']}")

                enrichment = self.enrich_with_semantic_scholar(paper['paper_id'])

                if enrichment:
                    paper.update(enrichment)
                    enriched_count += 1

            logger.info(f"✓ Enriched {enriched_count}/{len(papers)} papers with citation data")
            logger.info("")

        # Send papers to processing service
        logger.info("Step 3: Sending papers to processing service...")
        success_count = 0
        failure_count = 0

        for i, paper in enumerate(papers, 1):
            logger.info(f"Processing paper {i}/{len(papers)}: {paper['paper_id']}")

            if self.send_to_processing_service(paper):
                success_count += 1
            else:
                failure_count += 1

            # Small delay between processing service calls
            if i < len(papers):
                time.sleep(1.0)

        logger.info("")
        logger.info("="*60)
        logger.info("Ingestion complete!")
        logger.info("="*60)
        logger.info(f"Success: {success_count}")
        logger.info(f"Failed: {failure_count}")
        logger.info(f"Total: {len(papers)}")
        logger.info(f"Enriched with citations: {enriched_count if enrich_with_citations else 0}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest papers from arXiv with proper rate limiting"
    )
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
    parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Skip Semantic Scholar citation enrichment"
    )

    args = parser.parse_args()

    # Create ingestion handler
    ingestion = ImprovedArxivIngestion(processing_service_url=args.processing_url)

    # Run ingestion
    try:
        ingestion.ingest_papers(
            categories=args.categories,
            max_results=args.max_results,
            days_back=args.days_back,
            enrich_with_citations=not args.no_citations
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
