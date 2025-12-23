"""Response generation using OpenAI GPT-4."""
import logging
from typing import List
from openai import OpenAI
from app.config import Settings
from app.schemas import PaperSource
from app.prompts import build_rag_prompt

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates responses using GPT-4 with retrieved context."""

    def __init__(self, settings: Settings):
        """Initialize the generator."""
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

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

            # Build prompts using modular prompt templates
            system_prompt, user_prompt = build_rag_prompt(query, papers)

            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
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
