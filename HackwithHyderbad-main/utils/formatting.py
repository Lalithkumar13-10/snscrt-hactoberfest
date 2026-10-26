"""Formatting utilities for IncidentIQ UI."""
from datetime import datetime


def format_timestamp(ts: str | None = None) -> str:
    """Return a human-readable timestamp."""
    if ts:
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return ts
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_memory_for_display(memory: dict) -> dict:
    """Format a raw memory dict for UI display."""
    return {
        "content": memory.get("text", memory.get("content", "No content")),
        "metadata": memory.get("metadata", {}),
        "tags": memory.get("tags", []),
    }


def severity_color(severity: str) -> str:
    """Return a color indicator for severity levels."""
    mapping = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }
    return mapping.get(severity.lower(), "⚪")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
