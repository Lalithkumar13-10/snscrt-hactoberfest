"""Groq LLM Client — Reasoning and generation layer for IncidentIQ.

Encapsulates all Groq API interactions. Agents call this module
for LLM-powered analysis and recommendations.
"""
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when a Groq operation fails."""
    pass


class GroqClient:
    """Encapsulates Groq SDK for LLM operations."""

    def __init__(self, api_key: str, model: str):
        self.model = model
        self._connected = False
        try:
            self.client = Groq(api_key=api_key)
            self._connected = True
            logger.info(f"Groq client initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise LLMError(f"Could not connect to Groq: {e}")

    @property
    def is_connected(self) -> bool:
        return self._connected

    def generate(self, system_prompt: str, user_prompt: str,
                 json_mode: bool = True, temperature: float = 0.3,
                 max_retries: int = 2) -> dict | str:
        """Generate a response from the LLM.

        Args:
            system_prompt: System-level instructions.
            user_prompt: User-level input with context.
            json_mode: If True, request JSON output.
            temperature: Sampling temperature.
            max_retries: Number of retries for transient errors.

        Returns:
            Parsed JSON dict if json_mode, otherwise raw string.
        """
        import time

        kwargs = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "model": self.model,
            "temperature": temperature,
            "max_tokens": 4096,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content

                if json_mode:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logger.warning("LLM returned non-JSON despite json_mode. Returning raw text.")
                        return {"raw_response": content}
                return content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_transient = any(keyword in error_str for keyword in [
                    "connection error", "timeout", "rate limit",
                    "getaddrinfo", "503", "429", "server error",
                ])
                if is_transient and attempt < max_retries:
                    wait = 2 * (attempt + 1)
                    logger.warning(f"Groq transient error (attempt {attempt + 1}): {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                logger.error(f"Groq generation failed: {e}")
                raise LLMError(f"LLM request failed: {e}")

    def test_connection(self) -> tuple[bool, str]:
        """Test the Groq connection with a minimal request."""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Reply with: OK"}],
                model=self.model,
                max_tokens=10,
            )
            reply = response.choices[0].message.content
            return True, f"Connected to Groq ({self.model}). Test reply: {reply}"
        except Exception as e:
            return False, f"Groq connection failed: {e}"
