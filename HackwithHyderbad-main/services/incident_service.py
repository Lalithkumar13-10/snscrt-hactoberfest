"""Incident Response Service — Orchestrates the incident analysis workflow."""
import logging
from memory.hindsight_memory import HindsightMemory
from llm.groq_client import GroqClient
from agents.incident_agent import (
    INCIDENT_SYSTEM_PROMPT,
    INCIDENT_AGENT_TYPE,
    build_incident_prompt,
    build_incident_memory_content,
    build_incident_memory_metadata,
    build_incident_recall_query,
)

logger = logging.getLogger(__name__)


class IncidentService:
    """Orchestrates incident analysis: Recall -> Analyze -> Retain."""

    def __init__(self, memory: HindsightMemory, llm: GroqClient):
        self.memory = memory
        self.llm = llm

    def analyze_incident(self, incident_data: dict) -> dict:
        """Analyze an incident using Hindsight memories and Groq.

        Returns:
            dict with keys: 'analysis', 'memories', 'memories_count'
        """
        # Step 1: Recall relevant past incidents from Hindsight
        query = build_incident_recall_query(incident_data)
        memories = []
        try:
            memories = self.memory.recall(query, agent_type=INCIDENT_AGENT_TYPE)
        except Exception as e:
            logger.error(f"Memory recall failed: {e}")

        # Step 2: Format memories for LLM context
        memories_text = self.memory.format_memories_for_llm(memories)

        # Step 3: Build prompt and get LLM analysis
        user_prompt = build_incident_prompt(incident_data, memories_text)
        analysis = self.llm.generate(
            system_prompt=INCIDENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_mode=True,
        )

        return {
            "analysis": analysis,
            "memories": memories,
            "memories_count": len(memories),
        }

    def resolve_and_learn(self, incident_data: dict, resolution_data: dict) -> bool:
        """Store a resolved incident as a new memory in Hindsight.

        Returns:
            True if memory was stored successfully.
        """
        content = build_incident_memory_content(incident_data, resolution_data)
        metadata = build_incident_memory_metadata(incident_data)
        tags = [
            incident_data.get("service", ""),
            incident_data.get("severity", ""),
            incident_data.get("environment", ""),
        ]
        tags = [t for t in tags if t]  # Remove empty

        return self.memory.retain(
            content=content,
            agent_type=INCIDENT_AGENT_TYPE,
            metadata=metadata,
            tags=tags,
        )
