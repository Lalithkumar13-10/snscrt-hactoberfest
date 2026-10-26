import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when a required configuration variable is missing."""
    pass


def _get_required(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise ConfigError(f"Required environment variable '{key}' is missing or empty. Check your .env file.")
    return value


def get_config() -> dict:
    """Load and validate all required configuration values."""
    try:
        default_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
        config = {
            "HINDSIGHT_API_KEY": _get_required("HINDSIGHT_API_KEY"),
            "HINDSIGHT_BASE_URL": _get_required("HINDSIGHT_BASE_URL"),
            "HINDSIGHT_BANK_ID": _get_required("HINDSIGHT_BANK_ID"),
            "GROQ_API_KEY": _get_required("GROQ_API_KEY"),
            "GROQ_MODEL": default_model,
            # Dedicated models per agent
            "GROQ_MODEL_INCIDENT": os.getenv("GROQ_MODEL_INCIDENT", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b",
            "GROQ_MODEL_CODE_REVIEW": os.getenv("GROQ_MODEL_CODE_REVIEW", "qwen/qwen3.8-27b").strip() or "qwen/qwen3.8-27b",
            "GROQ_MODEL_PIPELINE": os.getenv("GROQ_MODEL_PIPELINE", "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b",
            "APP_NAME": os.getenv("APP_NAME", "IncidentIQ"),
            "APP_ENV": os.getenv("APP_ENV", "development"),
        }
        logger.info("Configuration loaded successfully.")
        return config
    except ConfigError:
        raise


def validate_config() -> tuple[bool, list[str]]:
    """Validate config and return (is_valid, list_of_errors)."""
    errors = []
    required_keys = [
        "HINDSIGHT_API_KEY", "HINDSIGHT_BASE_URL", "HINDSIGHT_BANK_ID",
        "GROQ_API_KEY",
    ]
    for key in required_keys:
        value = os.getenv(key, "").strip()
        if not value:
            errors.append(f"Missing: {key}")
    return (len(errors) == 0, errors)
