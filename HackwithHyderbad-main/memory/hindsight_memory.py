"""Hindsight Memory Service — Central persistent memory layer for IncidentIQ.

All Hindsight operations (retain, recall, reflect) are encapsulated here.
Agents and services call this module instead of using the Hindsight SDK directly.
"""
import logging
import warnings
from datetime import datetime, timezone
from hindsight_client import Hindsight

warnings.filterwarnings("ignore", category=ResourceWarning)

logger = logging.getLogger(__name__)


class MemoryError(Exception):
    """Raised when a Hindsight operation fails."""
    pass


class HindsightMemory:
    """Encapsulates Hindsight client and provides thread-safe memory operations."""

    def __init__(self, api_key: str, base_url: str, bank_id: str):
        self.api_key = api_key
        self.base_url = base_url
        self.bank_id = bank_id
        self._connected = False
        try:
            client = self._get_client()
            self._connected = True
            logger.info(f"Hindsight client initialized for bank: {bank_id}")
            try:
                client.close()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Failed to initialize Hindsight client: {e}")
            raise MemoryError(f"Could not connect to Hindsight: {e}")

    def _get_client(self) -> Hindsight:
        """Create a fresh Hindsight client bound to the current thread and event loop.

        This prevents aiohttp 'Timeout context manager should be used inside a task'
        errors when Streamlit runs callbacks/actions in different worker threads.
        """
        return Hindsight(base_url=self.base_url, api_key=self.api_key)

    @property
    def client(self) -> Hindsight:
        """Property returning a client for compatibility."""
        return self._get_client()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def retain(self, content: str, agent_type: str, metadata: dict | None = None,
               tags: list[str] | None = None) -> bool:
        """Store a new memory in Hindsight.

        Args:
            content: Natural-language description of the experience.
            agent_type: One of 'incident_response', 'code_review', 'devops_pipeline'.
            metadata: Optional dict of structured metadata.
            tags: Optional list of string tags.

        Returns:
            True if retained successfully, False otherwise.
        """
        if not content or not content.strip():
            logger.warning("Attempted to retain empty content. Skipping.")
            return False

        full_metadata = {
            "agent_type": agent_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            for k, v in metadata.items():
                full_metadata[str(k)] = str(v)

        full_tags = [agent_type]
        if tags:
            full_tags.extend(tags)

        client = self._get_client()
        try:
            client.retain(
                bank_id=self.bank_id,
                content=content,
                metadata=full_metadata,
                tags=full_tags,
            )
            logger.info(f"Memory retained for agent '{agent_type}': {content[:80]}...")
            return True
        except Exception as e:
            logger.error(f"Hindsight retain failed: {e}")
            raise MemoryError(f"Failed to store memory: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass

    def recall(self, query: str, agent_type: str | None = None,
              max_results: int = 5) -> list[dict]:
        """Recall relevant memories from Hindsight.

        Args:
            query: Natural-language search query.
            agent_type: Optional filter — if set, the query is prefixed
                        with agent context for more relevant results.
            max_results: Maximum number of results to return.

        Returns:
            List of memory dicts with 'content', 'metadata', 'tags' keys.
        """
        if not query or not query.strip():
            return []

        # Prefix query with agent context for better semantic recall
        search_query = query
        if agent_type:
            agent_labels = {
                "incident_response": "production incident, root cause, resolution, postmortem",
                "code_review": "code review, team coding preference, architecture standard",
                "devops_pipeline": "deployment failure, build failure, pipeline, infrastructure",
            }
            prefix = agent_labels.get(agent_type, "")
            if prefix:
                search_query = f"[{prefix}] {query}"

        client = self._get_client()
        try:
            results = client.recall(
                bank_id=self.bank_id,
                query=search_query,
            )

            memories = []
            result_list = results.results if hasattr(results, 'results') else (results if isinstance(results, list) else [])
            for item in result_list[:max_results]:
                memory = {
                    "content": getattr(item, 'text', None) or getattr(item, 'content', str(item)),
                    "metadata": getattr(item, 'metadata', {}),
                    "tags": getattr(item, 'tags', []),
                }
                memories.append(memory)

            logger.info(f"Recalled {len(memories)} memories for query: {query[:60]}")
            return memories
        except Exception as e:
            logger.error(f"Hindsight recall failed: {e}")
            raise MemoryError(f"Failed to recall memories: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass

    def reflect(self, query: str) -> str | None:
        """Synthesize memories into a reasoned summary.

        Args:
            query: The question or topic to reflect on.

        Returns:
            A synthesized summary string, or None on failure.
        """
        client = self._get_client()
        try:
            summary = client.reflect(
                bank_id=self.bank_id,
                query=query,
            )
            return str(summary) if summary else None
        except Exception as e:
            logger.warning(f"Hindsight reflect failed (non-critical): {e}")
            return None
        finally:
            try:
                client.close()
            except Exception:
                pass

    def format_memories_for_llm(self, memories: list[dict]) -> str:
        """Format recalled memories into a text block for LLM context."""
        if not memories:
            return "No relevant previous memories found."

        lines = [f"--- {len(memories)} Relevant Past Memories ---"]
        for i, mem in enumerate(memories, 1):
            lines.append(f"\nMemory #{i}:")
            lines.append(mem.get("content", "No content"))
            meta = mem.get("metadata", {})
            if meta:
                meta_str = ", ".join(f"{k}: {v}" for k, v in meta.items()
                                     if k not in ("timestamp",))
                if meta_str:
                    lines.append(f"  Context: {meta_str}")
        lines.append("--- End of Memories ---")
        return "\n".join(lines)

    def test_connection(self) -> tuple[bool, str]:
        """Test the Hindsight connection by performing a harmless recall."""
        client = self._get_client()
        try:
            client.recall(bank_id=self.bank_id, query="connection test")
            return True, "Connected to Hindsight successfully."
        except Exception as e:
            return False, f"Hindsight connection failed: {e}"
        finally:
            try:
                client.close()
            except Exception:
                pass

    def close(self):
        """Close any lingering client sessions."""
        pass
