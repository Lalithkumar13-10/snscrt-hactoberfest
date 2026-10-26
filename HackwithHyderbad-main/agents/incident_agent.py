"""Incident Response Agent — Analyzes production incidents using Hindsight memory."""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

INCIDENT_SYSTEM_PROMPT = """You are an expert Incident Response AI Agent for IncidentIQ.
You help DevOps engineers and SREs analyze production incidents.

You will receive:
1. Current incident details
2. Relevant past incident memories from Hindsight (if any exist)

Your job:
- Analyze the current incident
- If past memories are provided, use them to inform your analysis
- Identify likely root cause hypotheses
- Recommend specific actions
- Reference historical evidence from past memories when applicable
- Be honest: if no relevant past experience exists, say so clearly

IMPORTANT:
- Do NOT fabricate historical evidence
- If memories are provided, reference them specifically
- If no memories are provided, give a fresh analysis and say "No relevant previous memory was found."
- Clearly distinguish between evidence-based recommendations and general best practices

Respond ONLY in this JSON format:
{
  "summary": "Brief incident summary",
  "root_cause_hypothesis": "Most likely root cause based on analysis and history",
  "recommended_actions": ["Action 1", "Action 2", ...],
  "historical_evidence": ["Evidence from past memory 1", ...],
  "risk_notes": ["Risk or warning 1", ...],
  "memory_influence": "Description of how past memories influenced this recommendation, or 'No previous memories influenced this analysis'"
}"""


def build_incident_prompt(incident_data: dict, memories_text: str) -> str:
    """Build the user prompt for incident analysis."""
    prompt = f"""## Current Incident

Incident ID: {incident_data.get('incident_id', 'N/A')}
Service: {incident_data.get('service', 'N/A')}
Severity: {incident_data.get('severity', 'N/A')}
Environment: {incident_data.get('environment', 'N/A')}
Error Title: {incident_data.get('error_title', 'N/A')}
Description: {incident_data.get('description', 'N/A')}

## Past Experience from Hindsight Memory

{memories_text}

## Task

Analyze this incident. Use any relevant past memories to provide context-aware recommendations.
If past memories are relevant, explain HOW they influenced your recommendation.
If no relevant past memories exist, provide a fresh analysis and clearly state that.
"""
    return prompt


def build_incident_memory_content(incident_data: dict, resolution_data: dict) -> str:
    """Build natural-language memory content for storing a resolved incident."""
    return f"""Incident {incident_data.get('incident_id', 'N/A')} occurred in the {incident_data.get('service', 'unknown service')} service on {incident_data.get('environment', 'unknown environment')}.
Severity: {incident_data.get('severity', 'N/A')}.
Error: {incident_data.get('error_title', 'N/A')}.
Description: {incident_data.get('description', 'N/A')}.
Root Cause: {resolution_data.get('root_cause', 'Not specified')}.
Resolution: {resolution_data.get('resolution', 'Not specified')}.
Outcome: {resolution_data.get('outcome', 'Not specified')}.
Lesson Learned: {resolution_data.get('lesson_learned', 'Not specified')}."""


def build_incident_memory_metadata(incident_data: dict) -> dict:
    """Build metadata for an incident memory."""
    return {
        "incident_id": incident_data.get("incident_id", ""),
        "service": incident_data.get("service", ""),
        "severity": incident_data.get("severity", ""),
        "environment": incident_data.get("environment", ""),
    }


def build_incident_recall_query(incident_data: dict) -> str:
    """Build a recall query for finding similar past incidents."""
    parts = []
    if incident_data.get("service"):
        parts.append(f"service {incident_data['service']}")
    if incident_data.get("error_title"):
        parts.append(f"error {incident_data['error_title']}")
    if incident_data.get("description"):
        parts.append(incident_data["description"])
    if incident_data.get("environment"):
        parts.append(f"environment {incident_data['environment']}")
    return " ".join(parts) if parts else "production incident"


INCIDENT_AGENT_TYPE = "incident_response"
