"""Code Review Service — Orchestrates the code review workflow."""
import logging
from memory.hindsight_memory import HindsightMemory
from llm.groq_client import GroqClient
from agents.code_review_agent import (
    CODE_REVIEW_SYSTEM_PROMPT,
    CODE_REVIEW_AGENT_TYPE,
    build_code_review_prompt,
    build_code_review_memory_content,
    build_code_review_memory_metadata,
    build_code_review_recall_query,
)

logger = logging.getLogger(__name__)


class CodeReviewService:
    """Orchestrates code review: Recall -> Review -> Retain."""

    def __init__(self, memory: HindsightMemory, llm: GroqClient):
        self.memory = memory
        self.llm = llm

    def review_code(self, review_data: dict) -> dict:
        """Review code using Hindsight team memories and Groq.

        Returns:
            dict with keys: 'review', 'memories', 'memories_count'
        """
        # Step 1: Recall relevant team preferences from Hindsight
        query = build_code_review_recall_query(review_data)
        memories = []
        try:
            memories = self.memory.recall(query, agent_type=CODE_REVIEW_AGENT_TYPE)
        except Exception as e:
            logger.error(f"Memory recall failed: {e}")

        # Step 2: Format memories for LLM context
        memories_text = self.memory.format_memories_for_llm(memories)

        # Step 3: Build prompt and get LLM review
        user_prompt = build_code_review_prompt(review_data, memories_text)
        review = self.llm.generate(
            system_prompt=CODE_REVIEW_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_mode=True,
        )

        return {
            "review": review,
            "memories": memories,
            "memories_count": len(memories),
        }

    def save_review_learning(self, review_data: dict, feedback: str) -> bool:
        """Store code review feedback as a new memory in Hindsight.

        Returns:
            True if memory was stored successfully.
        """
        content = build_code_review_memory_content(review_data, feedback)
        metadata = build_code_review_memory_metadata(review_data)
        tags = [
            review_data.get("language", ""),
            review_data.get("repository", ""),
        ]
        tags = [t for t in tags if t]

        return self.memory.retain(
            content=content,
            agent_type=CODE_REVIEW_AGENT_TYPE,
            metadata=metadata,
            tags=tags,
        )
