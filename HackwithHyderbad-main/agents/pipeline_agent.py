"""DevOps Pipeline Agent — Analyzes deployment/pipeline failures using Hindsight memory."""
import logging

logger = logging.getLogger(__name__)

PIPELINE_SYSTEM_PROMPT = """You are an expert DevOps Pipeline AI Agent for IncidentIQ.
You help DevOps and platform engineers diagnose deployment and pipeline failures.

You will receive:
1. Current deployment/pipeline details
2. Build and deployment status
3. Error logs
4. Infrastructure changes
5. Relevant past deployment memories from Hindsight (if any exist)

Your job:
- Analyze the current deployment/pipeline failure
- If past deployment memories are provided, use them to inform your analysis
- Identify likely causes
- Recommend investigation steps
- Suggest recovery or rollback actions
- Reference historical evidence when applicable

IMPORTANT:
- Do NOT fabricate historical evidence
- If memories are provided, reference them specifically
- If no memories exist, give a fresh analysis and say "No relevant previous memory was found."

Respond ONLY in this JSON format:
{
  "summary": "Brief deployment issue summary",
  "likely_causes": ["Cause 1", "Cause 2", ...],
  "investigation_steps": ["Step 1", "Step 2", ...],
  "recovery_actions": ["Action 1", "Action 2", ...],
  "historical_evidence": ["Evidence from past memory 1", ...],
  "memory_influence": "Description of how past memories influenced this recommendation, or 'No previous memories influenced this analysis'"
}"""


def build_pipeline_prompt(pipeline_data: dict, memories_text: str) -> str:
    """Build the user prompt for pipeline analysis."""
    prompt = f"""## Current Deployment / Pipeline

Pipeline/Deployment ID: {pipeline_data.get('pipeline_id', 'N/A')}
Service: {pipeline_data.get('service', 'N/A')}
Version: {pipeline_data.get('version', 'N/A')}
Environment: {pipeline_data.get('environment', 'N/A')}
Build Status: {pipeline_data.get('build_status', 'N/A')}
Deployment Status: {pipeline_data.get('deployment_status', 'N/A')}
Error Logs: {pipeline_data.get('error_logs', 'None')}
Infrastructure Changes: {pipeline_data.get('infra_changes', 'None')}

## Past Deployment Experience from Hindsight Memory

{memories_text}

## Task

Analyze this deployment/pipeline issue. Use any relevant past memories to provide context-aware recommendations.
If past memories are relevant, explain HOW they influenced your recommendation.
If no relevant past memories exist, provide a fresh analysis and clearly state that.
"""
    return prompt


def build_pipeline_memory_content(pipeline_data: dict, resolution_data: dict) -> str:
    """Build natural-language memory content for storing a deployment outcome."""
    return f"""Deployment {pipeline_data.get('pipeline_id', 'N/A')} for {pipeline_data.get('service', 'unknown service')} version {pipeline_data.get('version', 'N/A')} on {pipeline_data.get('environment', 'unknown environment')}.
Build Status: {pipeline_data.get('build_status', 'N/A')}.
Deployment Status: {pipeline_data.get('deployment_status', 'N/A')}.
Error: {pipeline_data.get('error_logs', 'None')}.
Infrastructure Changes: {pipeline_data.get('infra_changes', 'None')}.
Root Cause: {resolution_data.get('root_cause', 'Not specified')}.
Resolution: {resolution_data.get('resolution', 'Not specified')}.
Outcome: {resolution_data.get('outcome', 'Not specified')}.
Lesson Learned: {resolution_data.get('lesson_learned', 'Not specified')}."""


def build_pipeline_memory_metadata(pipeline_data: dict) -> dict:
    """Build metadata for a pipeline memory."""
    return {
        "pipeline_id": pipeline_data.get("pipeline_id", ""),
        "service": pipeline_data.get("service", ""),
        "version": pipeline_data.get("version", ""),
        "environment": pipeline_data.get("environment", ""),
    }


def build_pipeline_recall_query(pipeline_data: dict) -> str:
    """Build a recall query for finding similar past deployments."""
    parts = []
    if pipeline_data.get("service"):
        parts.append(f"service {pipeline_data['service']}")
    if pipeline_data.get("error_logs"):
        parts.append(f"error {pipeline_data['error_logs'][:200]}")
    if pipeline_data.get("environment"):
        parts.append(f"environment {pipeline_data['environment']}")
    if pipeline_data.get("infra_changes"):
        parts.append(f"infrastructure {pipeline_data['infra_changes'][:200]}")
    return " ".join(parts) if parts else "deployment failure pipeline"


PIPELINE_AGENT_TYPE = "devops_pipeline"
