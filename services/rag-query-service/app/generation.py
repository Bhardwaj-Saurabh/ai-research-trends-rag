"""Response generation using OpenAI GPT-4."""
import logging
from typing import List
from openai import OpenAI
from app.config import Settings
from app.schemas import PaperSource

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates responses using GPT-4 with retrieved context."""

    def __init__(self, settings: Settings):
        """Initialize the generator."""
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def build_context(self, papers: List[PaperSource]) -> str:
        """
        Build context string from retrieved papers.

        Args:
            papers: List of relevant papers

        Returns:
            Formatted context string
        """
        if not papers:
            return "No relevant papers found."

        context_parts = []
        for i, paper in enumerate(papers, 1):
            context_part = f"""
Paper {i}:
Title: {paper.title}
Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}
Published: {paper.published_date}
Citations: {paper.citation_count}
Abstract: {paper.abstract}
URL: {paper.arxiv_url}
""".strip()
            context_parts.append(context_part)

        context = "\n\n---\n\n".join(context_parts)
        return context

    def build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for GPT-4.

        Args:
            query: User's question
            context: Context from retrieved papers

        Returns:
            Complete prompt
        """
        prompt = f"""You are an AI research assistant helping users discover and understand AI research papers. You have access to a database of recent research papers and your task is to provide accurate, helpful answers based on the provided papers.

User Question: {query}

Relevant Research Papers:
{context}

Instructions:
1. Answer the user's question based ONLY on the provided papers above
2. Cite papers by their number (e.g., "According to Paper 1...")
3. If the papers don't contain enough information to fully answer the question, acknowledge this
4. Highlight key findings, methodologies, or trends mentioned in the papers
5. Be concise but thorough - aim for 2-4 paragraphs
6. Use clear, accessible language

Your Answer:"""

        return prompt

    def generate_response(
        self,
        query: str,
        papers: List[PaperSource]
    ) -> tuple[str, dict]:
        """
        Generate a response using GPT-4.

        Args:
            query: User's question
            papers: Retrieved papers for context

        Returns:
            Tuple of (generated_answer, metadata)
        """
        try:
            logger.info(f"Generating response for query: {query[:50]}...")

            # Build context and prompt
            context = self.build_context(papers)
            prompt = self.build_prompt(query, context)

            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI research assistant. Provide accurate, well-cited answers based on the research papers provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )

            answer = response.choices[0].message.content.strip()

            # Collect metadata
            metadata = {
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "papers_retrieved": len(papers)
            }

            logger.info(f"Response generated successfully. Tokens used: {metadata['tokens_used']}")

            return answer, metadata

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
