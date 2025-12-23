"""
Prompt templates for RAG query service.

All prompts are defined here to make them easy to modify and version control.
Can be overridden via environment variables or config files.
"""
import os
from typing import List
from app.schemas import PaperSource


class PromptTemplates:
    """Centralized prompt templates for the RAG system."""

    # System prompt for the AI assistant
    SYSTEM_PROMPT = os.getenv(
        "RAG_SYSTEM_PROMPT",
        "You are an expert AI research assistant. Provide accurate, well-cited answers based on the research papers provided."
    )

    # Main RAG prompt template
    RAG_PROMPT_TEMPLATE = os.getenv(
        "RAG_PROMPT_TEMPLATE",
        """You are an AI research assistant helping users discover and understand AI research papers. You have access to a database of recent research papers and your task is to provide accurate, helpful answers based on the provided papers.

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
    )

    # Alternative prompt for trend queries
    TREND_PROMPT_TEMPLATE = os.getenv(
        "RAG_TREND_PROMPT_TEMPLATE",
        """You are an AI research assistant specializing in identifying research trends. Analyze the provided papers to identify patterns, emerging themes, and developments.

User Question: {query}

Relevant Research Papers:
{context}

Instructions:
1. Identify common themes and trends across the papers
2. Highlight emerging methodologies or approaches
3. Note any significant shifts or developments in the field
4. Cite specific papers when discussing trends (e.g., "Paper 1 and Paper 3 both explore...")
5. Organize your response by trend or theme
6. Be specific and data-driven

Your Analysis:"""
    )

    # Comparison prompt
    COMPARISON_PROMPT_TEMPLATE = os.getenv(
        "RAG_COMPARISON_PROMPT_TEMPLATE",
        """You are an AI research assistant helping users compare different research approaches or papers.

User Question: {query}

Relevant Research Papers:
{context}

Instructions:
1. Compare and contrast the approaches described in the papers
2. Highlight similarities and differences
3. Discuss advantages and limitations of each approach
4. Cite specific papers for each point (e.g., "Paper 1 uses X while Paper 2 uses Y...")
5. Provide a balanced comparison
6. Be specific about technical details

Your Comparison:"""
    )

    @staticmethod
    def build_context(papers: List[PaperSource]) -> str:
        """
        Build context string from retrieved papers.

        Args:
            papers: List of relevant papers

        Returns:
            Formatted context string
        """
        if not papers:
            return "No relevant papers found."

        context_format = os.getenv(
            "RAG_CONTEXT_FORMAT",
            """Paper {index}:
Title: {title}
Authors: {authors}
Published: {published_date}
Citations: {citation_count}
Abstract: {abstract}
URL: {arxiv_url}"""
        )

        context_parts = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += f" et al. (+{len(paper.authors) - 3})"

            context_part = context_format.format(
                index=i,
                title=paper.title,
                authors=authors_str,
                published_date=paper.published_date,
                citation_count=paper.citation_count,
                abstract=paper.abstract,
                arxiv_url=paper.arxiv_url
            )
            context_parts.append(context_part.strip())

        separator = os.getenv("RAG_CONTEXT_SEPARATOR", "\n\n---\n\n")
        return separator.join(context_parts)

    @staticmethod
    def select_prompt_template(query: str) -> str:
        """
        Select appropriate prompt template based on query.

        Args:
            query: User's question

        Returns:
            Selected prompt template
        """
        query_lower = query.lower()

        # Trend detection keywords
        trend_keywords = ["trend", "emerging", "recent developments", "latest", "evolution"]
        if any(keyword in query_lower for keyword in trend_keywords):
            return PromptTemplates.TREND_PROMPT_TEMPLATE

        # Comparison keywords
        comparison_keywords = ["compare", "difference", "versus", "vs", "contrast"]
        if any(keyword in query_lower for keyword in comparison_keywords):
            return PromptTemplates.COMPARISON_PROMPT_TEMPLATE

        # Default to standard RAG prompt
        return PromptTemplates.RAG_PROMPT_TEMPLATE

    @staticmethod
    def build_prompt(query: str, context: str, template: str = None) -> str:
        """
        Build the complete prompt for GPT-4.

        Args:
            query: User's question
            context: Context from retrieved papers
            template: Optional specific template to use

        Returns:
            Complete prompt
        """
        if template is None:
            template = PromptTemplates.select_prompt_template(query)

        return template.format(query=query, context=context)


# Convenience functions
def get_system_prompt() -> str:
    """Get the system prompt."""
    return PromptTemplates.SYSTEM_PROMPT


def build_rag_prompt(query: str, papers: List[PaperSource]) -> tuple[str, str]:
    """
    Build system prompt and user prompt for RAG.

    Args:
        query: User's question
        papers: Retrieved papers

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    context = PromptTemplates.build_context(papers)
    user_prompt = PromptTemplates.build_prompt(query, context)
    system_prompt = PromptTemplates.SYSTEM_PROMPT

    return system_prompt, user_prompt

