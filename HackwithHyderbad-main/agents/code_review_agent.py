"""Code Review Agent — Reviews code using team-specific memories from Hindsight."""
import logging

logger = logging.getLogger(__name__)

CODE_REVIEW_SYSTEM_PROMPT = """You are an expert Code Review AI Agent for IncidentIQ.
You help developers and tech leads review code with team-specific context.

You will receive:
1. Source code to review
2. Programming language
3. Optional team/project context
4. Relevant team preferences and past review memories from Hindsight (if any exist)

Your job:
- Review the code for issues, best practices, and improvements
- If past team preferences are provided, apply them specifically
- Clearly separate GENERAL CODE PRACTICES from REMEMBERED TEAM PREFERENCES
- Be honest: if a suggestion is a general best practice, label it as such
- Do NOT pretend a generic coding rule is a remembered team preference

IMPORTANT:
- Do NOT fabricate team preferences
- If memories mention team-specific preferences, reference them
- If no team memories exist, say so and provide only general recommendations
- Clearly label each finding

Respond ONLY in this JSON format:
{
  "summary": "Brief review summary",
  "critical": [{"issue": "...", "location": "...", "suggestion": "...", "source": "general_practice or team_preference"}],
  "warnings": [{"issue": "...", "location": "...", "suggestion": "...", "source": "general_practice or team_preference"}],
  "suggestions": [{"issue": "...", "location": "...", "suggestion": "...", "source": "general_practice or team_preference"}],
  "team_preferences_applied": ["Preference 1 from memory", ...],
  "general_practices_applied": ["General practice 1", ...],
  "memory_influence": "Description of how past memories influenced this review, or 'No previous team memories influenced this review'"
}"""


def build_code_review_prompt(review_data: dict, memories_text: str) -> str:
    """Build the user prompt for code review."""
    prompt = f"""## Code to Review

Repository/Project: {review_data.get('repository', 'N/A')}
Programming Language: {review_data.get('language', 'N/A')}
Team Context: {review_data.get('team_context', 'None provided')}

```{review_data.get('language', '').lower()}
{review_data.get('code', 'No code provided')}
```

## Past Team Knowledge from Hindsight Memory

{memories_text}

## Task

Review this code. Apply any relevant team preferences from memory.
Clearly separate GENERAL CODE PRACTICES from REMEMBERED TEAM PREFERENCES.
If no team memories exist, state that clearly and provide only general recommendations.
"""
    return prompt


def build_code_review_memory_content(review_data: dict, feedback: str) -> str:
    """Build natural-language memory content for storing a code review outcome."""
    return f"""Code review for {review_data.get('repository', 'unknown project')} ({review_data.get('language', 'unknown language')}).
Team Context: {review_data.get('team_context', 'None')}.
Key Feedback: {feedback}."""


def build_code_review_memory_metadata(review_data: dict) -> dict:
    """Build metadata for a code review memory."""
    return {
        "repository": review_data.get("repository", ""),
        "language": review_data.get("language", ""),
    }


def build_code_review_recall_query(review_data: dict) -> str:
    """Build a recall query for finding relevant team preferences."""
    parts = []
    if review_data.get("repository"):
        parts.append(f"project {review_data['repository']}")
    if review_data.get("language"):
        parts.append(f"{review_data['language']} code review")
    if review_data.get("team_context"):
        parts.append(review_data["team_context"])
    parts.append("team coding preference convention standard")
    return " ".join(parts) if parts else "code review team preference"


CODE_REVIEW_AGENT_TYPE = "code_review"
