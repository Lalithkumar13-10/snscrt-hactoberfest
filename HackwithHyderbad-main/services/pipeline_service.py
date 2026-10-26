"""Pipeline Service — Orchestrates the DevOps pipeline analysis workflow."""
import logging
from memory.hindsight_memory import HindsightMemory
from llm.groq_client import GroqClient
from agents.pipeline_agent import (
    PIPELINE_SYSTEM_PROMPT,
    PIPELINE_AGENT_TYPE,
    build_pipeline_prompt,
    build_pipeline_memory_content,
    build_pipeline_memory_metadata,
    build_pipeline_recall_query,
)

logger = logging.getLogger(__name__)


class PipelineService:
    """Orchestrates pipeline analysis: Recall -> Analyze -> Retain."""

    def __init__(self, memory: HindsightMemory, llm: GroqClient):
        self.memory = memory
        self.llm = llm

    def analyze_pipeline(self, pipeline_data: dict) -> dict:
        """Analyze a pipeline/deployment using Hindsight memories and Groq.

        Returns:
            dict with keys: 'analysis', 'memories', 'memories_count'
        """
        # Step 1: Recall relevant past deployments from Hindsight
        query = build_pipeline_recall_query(pipeline_data)
        memories = []
        try:
            memories = self.memory.recall(query, agent_type=PIPELINE_AGENT_TYPE)
        except Exception as e:
            logger.error(f"Memory recall failed: {e}")

        # Step 2: Format memories for LLM context
        memories_text = self.memory.format_memories_for_llm(memories)

        # Step 3: Build prompt and get LLM analysis
        user_prompt = build_pipeline_prompt(pipeline_data, memories_text)
        analysis = self.llm.generate(
            system_prompt=PIPELINE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_mode=True,
        )

        return {
            "analysis": analysis,
            "memories": memories,
            "memories_count": len(memories),
        }

    def resolve_and_learn(self, pipeline_data: dict, resolution_data: dict) -> bool:
        """Store a resolved deployment as a new memory in Hindsight.

        Returns:
            True if memory was stored successfully.
        """
        content = build_pipeline_memory_content(pipeline_data, resolution_data)
        metadata = build_pipeline_memory_metadata(pipeline_data)
        tags = [
            pipeline_data.get("service", ""),
            pipeline_data.get("environment", ""),
        ]
        tags = [t for t in tags if t]

        return self.memory.retain(
            content=content,
            agent_type=PIPELINE_AGENT_TYPE,
            metadata=metadata,
            tags=tags,
        )
