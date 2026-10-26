"""IncidentIQ — Engineering Agents That Remember, Learn, and Improve.

Main Streamlit application providing a unified interface for three AI agents:
1. Incident Response Agent
2. Code Review Agent
3. DevOps Pipeline Agent

All agents use Hindsight as their persistent memory layer and Groq for LLM reasoning.
"""
import streamlit as st
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from utils.config import get_config, validate_config, ConfigError
from utils.formatting import severity_color, truncate_text
from memory.hindsight_memory import HindsightMemory, MemoryError
from llm.groq_client import GroqClient, LLMError
from services.incident_service import IncidentService
from services.code_review_service import CodeReviewService
from services.pipeline_service import PipelineService
from demo.demo_memories import load_demo_memories, get_demo_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Page Config ───
st.set_page_config(
    page_title="IncidentIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 { font-size: 2.4rem; margin-bottom: 0; }
    .main-header p { color: #888; font-size: 1.1rem; margin-top: 0.2rem; }
    .memory-card {
        background: #1e1e2e;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-ok { color: #4caf50; }
    .status-err { color: #f44336; }
    div[data-testid="stMetric"] { background: #1a1a2e; border-radius: 8px; padding: 0.8rem; }
</style>
""", unsafe_allow_html=True)


# ─── Initialize Session State ───
def init_session():
    defaults = {
        "initialized": False,
        "memory": None,
        "llm": None,
        "incident_service": None,
        "code_review_service": None,
        "pipeline_service": None,
        "hindsight_ok": False,
        "groq_ok": False,
        "config": None,
        "learning_timeline": [],
        "interaction_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─── Connect Services ───
def initialize_services():
    """Initialize Hindsight, Groq, and service layer."""
    if st.session_state.initialized:
        return

    try:
        config = get_config()
        st.session_state.config = config
    except ConfigError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.stop()

    # Hindsight
    try:
        memory = HindsightMemory(
            api_key=config["HINDSIGHT_API_KEY"],
            base_url=config["HINDSIGHT_BASE_URL"],
            bank_id=config["HINDSIGHT_BANK_ID"],
        )
        ok, msg = memory.test_connection()
        st.session_state.memory = memory
        st.session_state.hindsight_ok = ok
    except MemoryError as e:
        st.session_state.hindsight_ok = False
        logger.error(f"Hindsight init failed: {e}")

    # Groq
    try:
        llm = GroqClient(
            api_key=config["GROQ_API_KEY"],
            model=config["GROQ_MODEL"],
        )
        ok, msg = llm.test_connection()
        st.session_state.llm = llm
        st.session_state.groq_ok = ok
    except LLMError as e:
        st.session_state.groq_ok = False
        logger.error(f"Groq init failed: {e}")

    # Services
    if st.session_state.memory and st.session_state.llm:
        st.session_state.incident_service = IncidentService(
            st.session_state.memory, st.session_state.llm
        )
        st.session_state.code_review_service = CodeReviewService(
            st.session_state.memory, st.session_state.llm
        )
        st.session_state.pipeline_service = PipelineService(
            st.session_state.memory, st.session_state.llm
        )

    st.session_state.initialized = True


initialize_services()


# ─── Sidebar ───
with st.sidebar:
    st.markdown("### ⚙️ System Status")

    if st.session_state.hindsight_ok:
        st.markdown("🟢 **Hindsight Connected**")
    else:
        st.markdown("🔴 **Hindsight Connection Failed**")
        st.caption("Check HINDSIGHT_API_KEY and HINDSIGHT_BASE_URL in your .env file.")

    if st.session_state.groq_ok:
        st.markdown("🟢 **Groq Connected**")
    else:
        st.markdown("🔴 **Groq Connection Failed**")
        st.caption("Check GROQ_API_KEY and GROQ_MODEL in your .env file.")

    if st.session_state.config:
        st.markdown(f"🧠 **Memory Bank:** `{st.session_state.config.get('HINDSIGHT_BANK_ID', 'N/A')}`")
        st.markdown(f"🤖 **Model:** `{st.session_state.config.get('GROQ_MODEL', 'N/A')}`")

    st.divider()

    # Demo Controls
    st.markdown("### 🎮 Demo Controls")
    if st.button("📦 Load Demo Memories", use_container_width=True):
        if st.session_state.memory:
            with st.spinner("Loading demo memories into Hindsight..."):
                stats = load_demo_memories(st.session_state.memory)
            st.success(f"✅ Loaded: {stats['loaded']} | Skipped: {stats['skipped']} | Errors: {stats['errors']}")
            if stats["details"]:
                with st.expander("Details"):
                    for d in stats["details"]:
                        st.caption(d)
        else:
            st.error("Hindsight not connected. Cannot load demo memories.")

    st.divider()

    # Learning Timeline
    st.markdown("### 📈 Learning Timeline")
    if st.session_state.learning_timeline:
        for entry in st.session_state.learning_timeline[-10:]:
            icon = {"incident_response": "🚨", "code_review": "🔍", "devops_pipeline": "🚀"}.get(entry.get("agent"), "🧠")
            st.caption(f"{icon} **{entry.get('action', '')}**")
            st.caption(f"   Memories recalled: {entry.get('memories_recalled', 0)}")
            st.caption(f"   {entry.get('timestamp', '')}")
            st.caption("---")
    else:
        st.caption("No interactions yet.")
        st.caption("Interaction 1 → No memory → Generic analysis")
        st.caption("Interaction 2 → Past recall → Better recommendations")
        st.caption("Interaction 3 → Multiple memories → Context-aware analysis")

    st.divider()
    st.caption(f"**{st.session_state.config.get('APP_NAME', 'IncidentIQ')}** v1.0")
    st.caption(f"Interactions: {st.session_state.interaction_count}")


# ─── Header ───
st.markdown('<div class="main-header"><h1>🧠 IncidentIQ</h1><p>Engineering agents that remember, learn, and improve.</p></div>', unsafe_allow_html=True)


# ─── Helper: Display Memories ───
def display_memories(memories: list, title: str = "🧠 Hindsight Memory"):
    """Display recalled memories in a structured format."""
    st.markdown(f"### {title}")
    if not memories:
        st.info("No relevant previous memories found for this query.")
        return

    st.success(f"**{len(memories)} relevant memory(ies) found**")
    for i, mem in enumerate(memories, 1):
        content = mem.get("content", "No content")
        metadata = mem.get("metadata", {})
        with st.expander(f"Memory #{i} — {truncate_text(content, 80)}", expanded=(i <= 2)):
            st.markdown(content)
            if metadata:
                cols = st.columns(min(len(metadata), 4))
                for j, (k, v) in enumerate(metadata.items()):
                    if k not in ("timestamp",) and v:
                        cols[j % len(cols)].caption(f"**{k}:** {v}")


# ─── Helper: Display Analysis ───
def display_analysis(analysis: dict, agent_type: str):
    """Display LLM analysis results."""
    if isinstance(analysis, str):
        st.markdown(analysis)
        return

    if "raw_response" in analysis:
        st.markdown(analysis["raw_response"])
        return

    if agent_type == "incident_response":
        st.markdown("### 🔬 AI Analysis")
        if analysis.get("summary"):
            st.markdown(f"**Summary:** {analysis['summary']}")
        if analysis.get("root_cause_hypothesis"):
            st.warning(f"**Root Cause Hypothesis:** {analysis['root_cause_hypothesis']}")
        if analysis.get("recommended_actions"):
            st.markdown("**Recommended Actions:**")
            for action in analysis["recommended_actions"]:
                st.markdown(f"  ✅ {action}")
        if analysis.get("historical_evidence"):
            st.markdown("**Historical Evidence:**")
            for evidence in analysis["historical_evidence"]:
                st.markdown(f"  📚 {evidence}")
        if analysis.get("risk_notes"):
            st.markdown("**Risk Notes:**")
            for note in analysis["risk_notes"]:
                st.markdown(f"  ⚠️ {note}")
        if analysis.get("memory_influence"):
            st.info(f"💡 **Memory Influence:** {analysis['memory_influence']}")

    elif agent_type == "code_review":
        st.markdown("### 🔬 AI Code Review")
        if analysis.get("summary"):
            st.markdown(f"**Summary:** {analysis['summary']}")
        if analysis.get("critical"):
            st.markdown("**🔴 Critical Issues:**")
            for item in analysis["critical"]:
                if isinstance(item, dict):
                    source_label = "🏷️ Team Preference" if item.get("source") == "team_preference" else "📘 General Practice"
                    st.error(f"**{item.get('issue', '')}** — {item.get('location', '')}\n\n💡 {item.get('suggestion', '')} | {source_label}")
                else:
                    st.error(str(item))
        if analysis.get("warnings"):
            st.markdown("**🟡 Warnings:**")
            for item in analysis["warnings"]:
                if isinstance(item, dict):
                    source_label = "🏷️ Team Preference" if item.get("source") == "team_preference" else "📘 General Practice"
                    st.warning(f"**{item.get('issue', '')}** — {item.get('location', '')}\n\n💡 {item.get('suggestion', '')} | {source_label}")
                else:
                    st.warning(str(item))
        if analysis.get("suggestions"):
            st.markdown("**🟢 Suggestions:**")
            for item in analysis["suggestions"]:
                if isinstance(item, dict):
                    source_label = "🏷️ Team Preference" if item.get("source") == "team_preference" else "📘 General Practice"
                    st.info(f"**{item.get('issue', '')}** — {item.get('location', '')}\n\n💡 {item.get('suggestion', '')} | {source_label}")
                else:
                    st.info(str(item))
        if analysis.get("team_preferences_applied"):
            st.markdown("**🏷️ Team-Specific Preferences Applied:**")
            for pref in analysis["team_preferences_applied"]:
                st.markdown(f"  🏷️ {pref}")
        if analysis.get("general_practices_applied"):
            st.markdown("**📘 General Practices Applied:**")
            for prac in analysis["general_practices_applied"]:
                st.markdown(f"  📘 {prac}")
        if analysis.get("memory_influence"):
            st.info(f"💡 **Memory Influence:** {analysis['memory_influence']}")

    elif agent_type == "devops_pipeline":
        st.markdown("### 🔬 AI Analysis")
        if analysis.get("summary"):
            st.markdown(f"**Summary:** {analysis['summary']}")
        if analysis.get("likely_causes"):
            st.markdown("**Likely Causes:**")
            for cause in analysis["likely_causes"]:
                st.warning(f"  🔍 {cause}")
        if analysis.get("investigation_steps"):
            st.markdown("**Investigation Steps:**")
            for step in analysis["investigation_steps"]:
                st.markdown(f"  🔧 {step}")
        if analysis.get("recovery_actions"):
            st.markdown("**Recovery / Rollback Actions:**")
            for action in analysis["recovery_actions"]:
                st.markdown(f"  ✅ {action}")
        if analysis.get("historical_evidence"):
            st.markdown("**Historical Evidence:**")
            for evidence in analysis["historical_evidence"]:
                st.markdown(f"  📚 {evidence}")
        if analysis.get("memory_influence"):
            st.info(f"💡 **Memory Influence:** {analysis['memory_influence']}")


# ─── Tabs ───
tab1, tab2, tab3 = st.tabs(["🚨 Incident Response", "🔍 Code Review", "🚀 DevOps Pipeline"])


# ══════════════════════════════════════════════════════════════
# TAB 1 — INCIDENT RESPONSE
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🚨 Incident Response Agent")
    st.caption("Analyze production incidents using past experience from Hindsight memory.")

    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        with col1:
            inc_id = st.text_input("Incident ID", placeholder="e.g., INC-005")
            inc_service = st.text_input("Service", placeholder="e.g., Payment API")
            inc_severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
        with col2:
            inc_env = st.text_input("Environment", placeholder="e.g., AWS Production")
            inc_error = st.text_input("Error / Incident Title", placeholder="e.g., HTTP 500 — Database timeout")
        inc_desc = st.text_area("Incident Description", height=100,
                                placeholder="Describe the incident in detail...")
        inc_submit = st.form_submit_button("🔍 Analyze Incident", use_container_width=True)

    if inc_submit:
        if not inc_desc.strip():
            st.error("Please provide an incident description.")
        elif not st.session_state.incident_service:
            st.error("Services not initialized. Check Hindsight and Groq connections.")
        else:
            incident_data = {
                "incident_id": inc_id or "N/A",
                "service": inc_service or "N/A",
                "severity": inc_severity,
                "environment": inc_env or "N/A",
                "error_title": inc_error or "N/A",
                "description": inc_desc,
            }
            st.session_state["current_incident"] = incident_data

            with st.spinner("🔍 Searching Hindsight for similar incidents & analyzing with AI..."):
                try:
                    result = st.session_state.incident_service.analyze_incident(incident_data)
                    st.session_state["incident_result"] = result
                    st.session_state.interaction_count += 1
                    st.session_state.learning_timeline.append({
                        "agent": "incident_response",
                        "action": f"Analyzed {inc_id or 'incident'}",
                        "memories_recalled": result["memories_count"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    })
                except (MemoryError, LLMError) as e:
                    st.error(f"Analysis failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # Display results
    if "incident_result" in st.session_state and st.session_state.get("incident_result"):
        result = st.session_state["incident_result"]

        st.markdown("---")
        st.markdown(f"### 📋 Current Incident: {st.session_state.get('current_incident', {}).get('incident_id', 'N/A')}")
        inc = st.session_state.get("current_incident", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Service", inc.get("service", "N/A"))
        c2.metric("Severity", inc.get("severity", "N/A"))
        c3.metric("Environment", inc.get("environment", "N/A"))
        c4.metric("Memories Found", result["memories_count"])

        display_memories(result["memories"], "🧠 Hindsight Memory — Similar Past Incidents")
        display_analysis(result["analysis"], "incident_response")

        # Resolve & Learn
        st.markdown("---")
        st.markdown("### ✅ Mark Resolved & Learn")
        with st.form("incident_resolve_form"):
            res_root = st.text_area("Actual Root Cause", placeholder="What was the actual root cause?")
            res_resolution = st.text_area("Resolution", placeholder="How was it resolved?")
            res_outcome = st.text_input("Outcome", placeholder="e.g., Service recovered in 10 minutes")
            res_lesson = st.text_area("Lesson Learned", placeholder="What should be remembered?")
            res_submit = st.form_submit_button("💾 Save & Learn", use_container_width=True)

        if res_submit:
            if not res_root.strip() or not res_resolution.strip():
                st.error("Please provide at least the root cause and resolution.")
            else:
                resolution_data = {
                    "root_cause": res_root,
                    "resolution": res_resolution,
                    "outcome": res_outcome or "Not specified",
                    "lesson_learned": res_lesson or "Not specified",
                }
                with st.spinner("💾 Storing experience in Hindsight..."):
                    try:
                        success = st.session_state.incident_service.resolve_and_learn(
                            st.session_state["current_incident"], resolution_data
                        )
                        if success:
                            st.success("✅ Experience stored in Hindsight! The agent will recall this in future incidents.")
                            st.session_state.learning_timeline.append({
                                "agent": "incident_response",
                                "action": f"Learned from {inc.get('incident_id', 'incident')}",
                                "memories_recalled": 0,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                            })
                            st.balloons()
                    except MemoryError as e:
                        st.error(f"Failed to store memory: {e}")


# ══════════════════════════════════════════════════════════════
# TAB 2 — CODE REVIEW
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🔍 Code Review Agent")
    st.caption("Review code using team-specific preferences remembered from Hindsight.")

    with st.form("code_review_form"):
        col1, col2 = st.columns(2)
        with col1:
            cr_repo = st.text_input("Repository / Project", placeholder="e.g., payment-api")
            cr_lang = st.selectbox("Programming Language", ["Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C#", "Other"])
        with col2:
            cr_context = st.text_area("Team Context (optional)", height=68,
                                      placeholder="e.g., Backend team, follows Clean Architecture")
        cr_code = st.text_area("Source Code", height=200,
                               placeholder="Paste your code here...")
        cr_submit = st.form_submit_button("🔍 Review Code", use_container_width=True)

    if cr_submit:
        if not cr_code.strip():
            st.error("Please provide source code to review.")
        elif not st.session_state.code_review_service:
            st.error("Services not initialized. Check Hindsight and Groq connections.")
        else:
            review_data = {
                "repository": cr_repo or "N/A",
                "language": cr_lang,
                "team_context": cr_context or "",
                "code": cr_code,
            }
            st.session_state["current_review"] = review_data

            with st.spinner("🔍 Searching Hindsight for team preferences & reviewing with AI..."):
                try:
                    result = st.session_state.code_review_service.review_code(review_data)
                    st.session_state["review_result"] = result
                    st.session_state.interaction_count += 1
                    st.session_state.learning_timeline.append({
                        "agent": "code_review",
                        "action": f"Reviewed code for {cr_repo or 'project'}",
                        "memories_recalled": result["memories_count"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    })
                except (MemoryError, LLMError) as e:
                    st.error(f"Review failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # Display results
    if "review_result" in st.session_state and st.session_state.get("review_result"):
        result = st.session_state["review_result"]

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Repository", st.session_state.get("current_review", {}).get("repository", "N/A"))
        c2.metric("Language", st.session_state.get("current_review", {}).get("language", "N/A"))
        c3.metric("Team Memories Found", result["memories_count"])

        display_memories(result["memories"], "🧠 Hindsight Memory — Team Knowledge")
        display_analysis(result["review"], "code_review")

        # Save Learning
        st.markdown("---")
        st.markdown("### 💾 Save Review Outcome")
        with st.form("code_review_save_form"):
            cr_feedback = st.text_area("Useful feedback to remember",
                                       placeholder="e.g., Team prefers async/await pattern for I/O operations")
            cr_save = st.form_submit_button("💾 Save & Learn", use_container_width=True)

        if cr_save:
            if not cr_feedback.strip():
                st.error("Please provide feedback to save.")
            else:
                with st.spinner("💾 Storing team knowledge in Hindsight..."):
                    try:
                        success = st.session_state.code_review_service.save_review_learning(
                            st.session_state["current_review"], cr_feedback
                        )
                        if success:
                            st.success("✅ Team knowledge stored in Hindsight! Future reviews will use this preference.")
                            st.session_state.learning_timeline.append({
                                "agent": "code_review",
                                "action": f"Learned preference for {st.session_state.get('current_review', {}).get('repository', 'project')}",
                                "memories_recalled": 0,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                            })
                            st.balloons()
                    except MemoryError as e:
                        st.error(f"Failed to store memory: {e}")


# ══════════════════════════════════════════════════════════════
# TAB 3 — DEVOPS PIPELINE
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🚀 DevOps Pipeline Agent")
    st.caption("Diagnose deployment and pipeline failures using historical experience from Hindsight.")

    with st.form("pipeline_form"):
        col1, col2 = st.columns(2)
        with col1:
            pl_id = st.text_input("Pipeline / Deployment ID", placeholder="e.g., DEP-005")
            pl_service = st.text_input("Service", placeholder="e.g., Order Service")
            pl_version = st.text_input("Version", placeholder="e.g., v2.5.0")
            pl_env = st.text_input("Environment", placeholder="e.g., AWS Production")
        with col2:
            pl_build = st.selectbox("Build Status", ["Passed", "Failed", "Unstable", "Unknown"])
            pl_deploy = st.selectbox("Deployment Status", ["Failed", "Partial", "Timeout", "Rollback", "Unknown"])
            pl_infra = st.text_area("Infrastructure Changes", height=68,
                                    placeholder="Any recent infra changes? e.g., Terraform update")
        pl_error = st.text_area("Error Logs", height=100,
                                placeholder="Paste relevant error logs...")
        pl_submit = st.form_submit_button("🔍 Analyze Pipeline", use_container_width=True)

    if pl_submit:
        if not pl_error.strip() and not pl_infra.strip():
            st.error("Please provide error logs or infrastructure changes to analyze.")
        elif not st.session_state.pipeline_service:
            st.error("Services not initialized. Check Hindsight and Groq connections.")
        else:
            pipeline_data = {
                "pipeline_id": pl_id or "N/A",
                "service": pl_service or "N/A",
                "version": pl_version or "N/A",
                "environment": pl_env or "N/A",
                "build_status": pl_build,
                "deployment_status": pl_deploy,
                "error_logs": pl_error or "None",
                "infra_changes": pl_infra or "None",
            }
            st.session_state["current_pipeline"] = pipeline_data

            with st.spinner("🔍 Searching Hindsight for similar deployments & analyzing with AI..."):
                try:
                    result = st.session_state.pipeline_service.analyze_pipeline(pipeline_data)
                    st.session_state["pipeline_result"] = result
                    st.session_state.interaction_count += 1
                    st.session_state.learning_timeline.append({
                        "agent": "devops_pipeline",
                        "action": f"Analyzed {pl_id or 'deployment'}",
                        "memories_recalled": result["memories_count"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    })
                except (MemoryError, LLMError) as e:
                    st.error(f"Analysis failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # Display results
    if "pipeline_result" in st.session_state and st.session_state.get("pipeline_result"):
        result = st.session_state["pipeline_result"]

        st.markdown("---")
        pl = st.session_state.get("current_pipeline", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Service", pl.get("service", "N/A"))
        c2.metric("Version", pl.get("version", "N/A"))
        c3.metric("Environment", pl.get("environment", "N/A"))
        c4.metric("Memories Found", result["memories_count"])

        display_memories(result["memories"], "🧠 Hindsight Memory — Historical Deployments")
        display_analysis(result["analysis"], "devops_pipeline")

        # Resolve & Learn
        st.markdown("---")
        st.markdown("### ✅ Deployment Resolved & Learn")
        with st.form("pipeline_resolve_form"):
            pl_root = st.text_area("Root Cause", placeholder="What caused the deployment failure?")
            pl_resolution = st.text_area("Resolution", placeholder="How was it resolved?")
            pl_outcome = st.text_input("Outcome", placeholder="e.g., Deployment succeeded after rollback")
            pl_lesson = st.text_area("Lesson Learned", placeholder="What should be remembered?")
            pl_res_submit = st.form_submit_button("💾 Save & Learn", use_container_width=True)

        if pl_res_submit:
            if not pl_root.strip() or not pl_resolution.strip():
                st.error("Please provide at least the root cause and resolution.")
            else:
                resolution_data = {
                    "root_cause": pl_root,
                    "resolution": pl_resolution,
                    "outcome": pl_outcome or "Not specified",
                    "lesson_learned": pl_lesson or "Not specified",
                }
                with st.spinner("💾 Storing deployment experience in Hindsight..."):
                    try:
                        success = st.session_state.pipeline_service.resolve_and_learn(
                            st.session_state["current_pipeline"], resolution_data
                        )
                        if success:
                            st.success("✅ Deployment experience stored in Hindsight! Future analyses will use this knowledge.")
                            st.session_state.learning_timeline.append({
                                "agent": "devops_pipeline",
                                "action": f"Learned from {pl.get('pipeline_id', 'deployment')}",
                                "memories_recalled": 0,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                            })
                            st.balloons()
                    except MemoryError as e:
                        st.error(f"Failed to store memory: {e}")


# ─── Footer ───
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#666;font-size:0.85rem;">'
    '🧠 IncidentIQ — Powered by <strong>Hindsight</strong> (persistent memory) + <strong>Groq</strong> (LLM reasoning)'
    '</div>',
    unsafe_allow_html=True,
)
