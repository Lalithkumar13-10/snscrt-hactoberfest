"""Basic validation tests for IncidentIQ.

Tests:
1. Configuration loading
2. Hindsight connection
3. Hindsight retain
4. Hindsight recall
5. Groq connection
6. Agent imports
7. Service imports

Usage:
    python test_hindsight.py
"""
import sys
import os

import warnings
warnings.filterwarnings("ignore")

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def test_config():
    """Test 1: Configuration loading."""
    print("\n=== Test 1: Configuration Loading ===")
    try:
        from utils.config import get_config, validate_config
        is_valid, errors = validate_config()
        if is_valid:
            print("  [PASS] All required environment variables are present.")
            config = get_config()
            print(f"  [PASS] App Name: {config['APP_NAME']}")
            print(f"  [PASS] Bank ID: {config['HINDSIGHT_BANK_ID']}")
            print(f"  [PASS] Groq Model: {config['GROQ_MODEL']}")
            return True
        else:
            print(f"  [FAIL] Configuration errors: {errors}")
            return False
    except Exception as e:
        print(f"  [FAIL] Config test failed: {e}")
        return False


def test_hindsight_connection():
    """Test 2: Hindsight connection."""
    print("\n=== Test 2: Hindsight Connection ===")
    try:
        from utils.config import get_config
        from memory.hindsight_memory import HindsightMemory
        config = get_config()
        memory = HindsightMemory(
            api_key=config["HINDSIGHT_API_KEY"],
            base_url=config["HINDSIGHT_BASE_URL"],
            bank_id=config["HINDSIGHT_BANK_ID"],
        )
        connected, msg = memory.test_connection()
        if connected:
            print(f"  [PASS] {msg}")
            return memory
        else:
            print(f"  [FAIL] {msg}")
            return None
    except Exception as e:
        print(f"  [FAIL] Hindsight connection failed: {e}")
        return None


def test_hindsight_retain(memory):
    """Test 3: Hindsight retain."""
    print("\n=== Test 3: Hindsight Retain ===")
    if not memory:
        print("  [SKIP] Skipped (no Hindsight connection)")
        return False
    try:
        result = memory.retain(
            content="IncidentIQ test memory: This is a controlled test memory created during validation. Test timestamp: validation-run.",
            agent_type="incident_response",
            metadata={"test": "true", "purpose": "validation"},
            tags=["test", "validation"],
        )
        if result:
            print("  [PASS] Memory retained successfully.")
            return True
        else:
            print("  [FAIL] Retain returned False.")
            return False
    except Exception as e:
        print(f"  [FAIL] Retain failed: {e}")
        return False


def test_hindsight_recall(memory):
    """Test 4: Hindsight recall."""
    print("\n=== Test 4: Hindsight Recall ===")
    if not memory:
        print("  [SKIP] Skipped (no Hindsight connection)")
        return False
    try:
        results = memory.recall(
            query="IncidentIQ test memory validation",
            agent_type="incident_response",
        )
        print(f"  [PASS] Recall returned {len(results)} result(s).")
        for i, r in enumerate(results[:3]):
            preview = r.get('content', 'N/A')[:80]
            print(f"     Memory {i+1}: {preview}...")
        return True
    except Exception as e:
        print(f"  [FAIL] Recall failed: {e}")
        return False


def test_groq_connection():
    """Test 5: Groq connection."""
    print("\n=== Test 5: Groq Connection ===")
    try:
        from utils.config import get_config
        from llm.groq_client import GroqClient
        config = get_config()
        llm = GroqClient(
            api_key=config["GROQ_API_KEY"],
            model=config["GROQ_MODEL"],
        )
        connected, msg = llm.test_connection()
        if connected:
            print(f"  [PASS] {msg}")
            return True
        else:
            print(f"  [FAIL] {msg}")
            return False
    except Exception as e:
        print(f"  [FAIL] Groq connection failed: {e}")
        return False


def test_agent_imports():
    """Test 6: Agent module imports."""
    print("\n=== Test 6: Agent Module Imports ===")
    success = True
    try:
        from agents.incident_agent import INCIDENT_SYSTEM_PROMPT, INCIDENT_AGENT_TYPE
        print("  [PASS] Incident Agent imported.")
    except Exception as e:
        print(f"  [FAIL] Incident Agent import failed: {e}")
        success = False
    try:
        from agents.code_review_agent import CODE_REVIEW_SYSTEM_PROMPT, CODE_REVIEW_AGENT_TYPE
        print("  [PASS] Code Review Agent imported.")
    except Exception as e:
        print(f"  [FAIL] Code Review Agent import failed: {e}")
        success = False
    try:
        from agents.pipeline_agent import PIPELINE_SYSTEM_PROMPT, PIPELINE_AGENT_TYPE
        print("  [PASS] Pipeline Agent imported.")
    except Exception as e:
        print(f"  [FAIL] Pipeline Agent import failed: {e}")
        success = False
    return success


def test_service_imports():
    """Test 7: Service module imports."""
    print("\n=== Test 7: Service Module Imports ===")
    success = True
    try:
        from services.incident_service import IncidentService
        print("  [PASS] IncidentService imported.")
    except Exception as e:
        print(f"  [FAIL] IncidentService import failed: {e}")
        success = False
    try:
        from services.code_review_service import CodeReviewService
        print("  [PASS] CodeReviewService imported.")
    except Exception as e:
        print(f"  [FAIL] CodeReviewService import failed: {e}")
        success = False
    try:
        from services.pipeline_service import PipelineService
        print("  [PASS] PipelineService imported.")
    except Exception as e:
        print(f"  [FAIL] PipelineService import failed: {e}")
        success = False
    return success


def main():
    print("=" * 60)
    print("  IncidentIQ - Validation Tests")
    print("=" * 60)

    results = {}

    results["config"] = test_config()
    memory = test_hindsight_connection()
    results["hindsight_connection"] = memory is not None
    results["hindsight_retain"] = test_hindsight_retain(memory)
    results["hindsight_recall"] = test_hindsight_recall(memory)
    results["groq_connection"] = test_groq_connection()
    results["agent_imports"] = test_agent_imports()
    results["service_imports"] = test_service_imports()

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}  {name}")
    print(f"\n  {passed}/{total} tests passed.")
    print("=" * 60)

    if memory:
        try:
            memory.close()
        except Exception:
            pass

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
