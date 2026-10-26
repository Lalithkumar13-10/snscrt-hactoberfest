"""Demo Memories — Realistic synthetic engineering experiences for hackathon demonstration.

Provides a controlled set of demo memories that can be loaded into Hindsight
to demonstrate the learning capabilities of IncidentIQ.
"""
import logging
import hashlib

logger = logging.getLogger(__name__)

# Each demo memory has a stable ID derived from its content to prevent duplicates
DEMO_MEMORIES = [
    # ==================== INCIDENT RESPONSE MEMORIES ====================
    {
        "agent_type": "incident_response",
        "content": (
            "Incident INC-001 occurred in the Payment API service on AWS production environment. "
            "The API returned HTTP 500 errors because the PostgreSQL database connection pool was exhausted. "
            "The team investigated and found that peak traffic at month-end caused connection pool saturation. "
            "The team increased the connection pool size from 50 to 100 connections. "
            "The service recovered successfully within 15 minutes after the configuration change. "
            "Lesson learned: Monitor database connection pool utilization during peak traffic periods "
            "and set up alerts when pool usage exceeds 80%."
        ),
        "metadata": {
            "incident_id": "INC-001",
            "service": "Payment API",
            "severity": "Critical",
            "environment": "AWS Production",
        },
        "tags": ["payment-api", "database", "connection-pool", "postgresql"],
    },
    {
        "agent_type": "incident_response",
        "content": (
            "Incident INC-002 occurred in the Authentication Service on AWS production. "
            "Users were unable to log in and received 401 Unauthorized errors. "
            "Investigation revealed that the JWT signing key was rotated during a scheduled maintenance window "
            "but the new key was not propagated to all service instances. "
            "The team performed a rolling restart of all Authentication Service instances to pick up the new key. "
            "Service was fully restored within 20 minutes. "
            "Lesson learned: Implement automated key propagation and verify all instances have the updated key "
            "before completing maintenance. Add a health check that validates JWT key consistency."
        ),
        "metadata": {
            "incident_id": "INC-002",
            "service": "Authentication Service",
            "severity": "Critical",
            "environment": "AWS Production",
        },
        "tags": ["authentication", "jwt", "key-rotation", "maintenance"],
    },
    {
        "agent_type": "incident_response",
        "content": (
            "Incident INC-003 occurred in the Order Service on AWS production. "
            "The service experienced intermittent Redis connection timeouts causing order processing delays. "
            "Root cause: The Redis cluster had undergone an infrastructure configuration change "
            "that modified the connection timeout settings from 5s to 1s. "
            "The team reverted the Redis timeout configuration to 5 seconds and added connection retry logic. "
            "Order processing returned to normal latency within 10 minutes. "
            "Lesson learned: Infrastructure configuration changes to shared services like Redis "
            "should be communicated to all dependent teams and tested under load before production deployment."
        ),
        "metadata": {
            "incident_id": "INC-003",
            "service": "Order Service",
            "severity": "High",
            "environment": "AWS Production",
        },
        "tags": ["order-service", "redis", "timeout", "infrastructure"],
    },
    {
        "agent_type": "incident_response",
        "content": (
            "Incident INC-004 occurred in the Payment API on AWS production. "
            "The API experienced repeated database connection timeout errors during business hours. "
            "Investigation showed that a recently deployed batch processing job was holding long-running "
            "database transactions, consuming available connections. "
            "The team moved the batch job to a dedicated database read replica and optimized query execution time. "
            "Database connection stability was restored. "
            "Lesson learned: Batch processing jobs should use separate database connections or read replicas "
            "to avoid impacting real-time API traffic."
        ),
        "metadata": {
            "incident_id": "INC-004",
            "service": "Payment API",
            "severity": "High",
            "environment": "AWS Production",
        },
        "tags": ["payment-api", "database", "timeout", "batch-processing"],
    },
    # ==================== CODE REVIEW MEMORIES ====================
    {
        "agent_type": "code_review",
        "content": (
            "Code review for the Payment API project (Python). "
            "Team preference: The team strongly prefers the Repository Pattern for all database access. "
            "Direct database queries in service classes are discouraged. "
            "All database operations should go through repository classes that encapsulate query logic. "
            "This was established as a team standard after multiple reviews identified inconsistent "
            "database access patterns across the codebase."
        ),
        "metadata": {
            "repository": "payment-api",
            "language": "Python",
        },
        "tags": ["repository-pattern", "database", "python", "architecture"],
    },
    {
        "agent_type": "code_review",
        "content": (
            "Code review for the Order Service project (Python). "
            "Team preference: The team avoids raw SQL queries in service classes. "
            "All database interactions must use the ORM (SQLAlchemy) or dedicated repository methods. "
            "Raw SQL is only acceptable in migration scripts or performance-critical batch operations "
            "with explicit team lead approval and documentation."
        ),
        "metadata": {
            "repository": "order-service",
            "language": "Python",
        },
        "tags": ["raw-sql", "orm", "python", "database"],
    },
    {
        "agent_type": "code_review",
        "content": (
            "Code review for backend services (Python). "
            "Team preference: All services must implement structured exception handling. "
            "Bare except clauses are prohibited. "
            "Custom exception classes should be used for domain-specific errors. "
            "All exceptions must be logged with appropriate severity level and context. "
            "HTTP APIs must return standardized error response format with error code, message, and request ID."
        ),
        "metadata": {
            "repository": "backend-services",
            "language": "Python",
        },
        "tags": ["exception-handling", "error-handling", "python", "standards"],
    },
    {
        "agent_type": "code_review",
        "content": (
            "Code review for microservices architecture (Python/Java). "
            "Team preference: Strict service/repository layer separation is required. "
            "Service classes contain business logic only. "
            "Repository classes handle all data access. "
            "Controller/API classes handle request/response mapping only. "
            "Cross-cutting concerns (logging, auth, metrics) use middleware or decorators, not inline code."
        ),
        "metadata": {
            "repository": "microservices",
            "language": "Python",
        },
        "tags": ["architecture", "separation-of-concerns", "service-repository", "microservices"],
    },
    # ==================== DEVOPS PIPELINE MEMORIES ====================
    {
        "agent_type": "devops_pipeline",
        "content": (
            "Deployment DEP-001 for Order Service v2.4.1 on AWS production. "
            "Build passed successfully but deployment failed with Redis connection timeout errors. "
            "Root cause: A recent infrastructure Terraform change modified the Redis security group rules, "
            "restricting inbound connections from the application subnet. "
            "Resolution: Rolled back the Terraform security group change and updated the IaC to include "
            "the correct application subnet CIDR. "
            "Outcome: Deployment succeeded after infrastructure rollback. "
            "Lesson learned: Infrastructure changes affecting shared services must include connectivity "
            "validation for all dependent applications before applying to production."
        ),
        "metadata": {
            "pipeline_id": "DEP-001",
            "service": "Order Service",
            "version": "v2.4.1",
            "environment": "AWS Production",
        },
        "tags": ["order-service", "redis", "terraform", "infrastructure"],
    },
    {
        "agent_type": "devops_pipeline",
        "content": (
            "Deployment DEP-002 for Payment API v3.1.0 on AWS staging. "
            "Build passed but deployment failed because required environment variables "
            "(STRIPE_API_KEY, PAYMENT_WEBHOOK_URL) were not configured in the staging environment. "
            "Root cause: The deployment pipeline did not validate required environment variables before deployment. "
            "Resolution: Added pre-deployment environment variable validation to the CI/CD pipeline "
            "and documented all required variables in the service README. "
            "Outcome: Deployment succeeded after adding the missing variables. "
            "Lesson learned: All deployments should include a pre-flight check that validates "
            "required environment variables are present in the target environment."
        ),
        "metadata": {
            "pipeline_id": "DEP-002",
            "service": "Payment API",
            "version": "v3.1.0",
            "environment": "AWS Staging",
        },
        "tags": ["payment-api", "environment-variables", "staging", "cicd"],
    },
    {
        "agent_type": "devops_pipeline",
        "content": (
            "Deployment DEP-003 for User Service v1.8.0 on Kubernetes production. "
            "Build passed but pods entered CrashLoopBackOff after deployment. "
            "Root cause: The new version required 512Mi memory but the Kubernetes resource limit was set to 256Mi. "
            "The application was OOM-killed repeatedly on startup. "
            "Resolution: Updated the Kubernetes deployment manifest to increase memory limit to 512Mi "
            "and added resource request/limit guidelines to the deployment checklist. "
            "Outcome: Pods started successfully after resource limit update. "
            "Lesson learned: Resource requirements should be profiled during staging deployment "
            "and Kubernetes manifests updated before production rollout."
        ),
        "metadata": {
            "pipeline_id": "DEP-003",
            "service": "User Service",
            "version": "v1.8.0",
            "environment": "Kubernetes Production",
        },
        "tags": ["kubernetes", "oom", "resource-limits", "crashloopbackoff"],
    },
    {
        "agent_type": "devops_pipeline",
        "content": (
            "Deployment DEP-004 for Notification Service v2.0.0 on AWS production. "
            "Build passed but deployment failed during database migration step. "
            "Root cause: The migration script attempted to add a NOT NULL column without a default value "
            "to an existing table with millions of rows. The migration timed out. "
            "Resolution: Modified the migration to add the column as nullable first, "
            "backfill existing rows, then add the NOT NULL constraint. "
            "Outcome: Migration completed successfully with zero downtime. "
            "Lesson learned: Database migrations on large tables should use multi-step approaches "
            "to avoid long-running locks and timeouts."
        ),
        "metadata": {
            "pipeline_id": "DEP-004",
            "service": "Notification Service",
            "version": "v2.0.0",
            "environment": "AWS Production",
        },
        "tags": ["database-migration", "timeout", "schema-change", "notification-service"],
    },
]


def _memory_hash(content: str) -> str:
    """Generate a stable hash from memory content to detect duplicates."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def load_demo_memories(memory_service) -> dict:
    """Load demo memories into Hindsight via the memory service.

    Uses content hashing to prevent duplicate insertion.
    First recalls existing memories to check for duplicates.

    Args:
        memory_service: HindsightMemory instance.

    Returns:
        dict with 'loaded', 'skipped', 'errors' counts.
    """
    stats = {"loaded": 0, "skipped": 0, "errors": 0, "details": []}

    for mem in DEMO_MEMORIES:
        mem_hash = _memory_hash(mem["content"])
        demo_tag = f"demo-{mem_hash}"

        try:
            # Check if this demo memory already exists by recalling with the unique hash
            existing = memory_service.recall(
                query=mem["content"][:100],
                agent_type=mem["agent_type"],
                max_results=3,
            )

            # Simple duplicate check: if we find a memory with very similar content, skip
            is_duplicate = False
            for existing_mem in existing:
                existing_content = existing_mem.get("content", "")
                # Check if the first 80 chars match (robust enough for demo data)
                if existing_content[:80] == mem["content"][:80]:
                    is_duplicate = True
                    break

            if is_duplicate:
                stats["skipped"] += 1
                stats["details"].append(f"Skipped (duplicate): {mem['agent_type']} - {mem['content'][:50]}...")
                continue

            # Retain the demo memory
            tags = mem.get("tags", []) + ["demo-data", demo_tag]
            memory_service.retain(
                content=mem["content"],
                agent_type=mem["agent_type"],
                metadata=mem.get("metadata", {}),
                tags=tags,
            )
            stats["loaded"] += 1
            stats["details"].append(f"Loaded: {mem['agent_type']} - {mem['content'][:50]}...")

        except Exception as e:
            stats["errors"] += 1
            stats["details"].append(f"Error: {mem['agent_type']} - {e}")
            logger.error(f"Failed to load demo memory: {e}")

    logger.info(f"Demo memories loaded: {stats['loaded']}, skipped: {stats['skipped']}, errors: {stats['errors']}")
    return stats


def get_demo_summary() -> list[dict]:
    """Get a summary of available demo memories for UI display."""
    summary = []
    for mem in DEMO_MEMORIES:
        summary.append({
            "agent_type": mem["agent_type"],
            "preview": mem["content"][:120] + "...",
            "metadata": mem.get("metadata", {}),
        })
    return summary
