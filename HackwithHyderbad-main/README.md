# IncidentIQ

**Engineering Agents That Remember, Learn, and Improve.**

---

## Problem

Engineering teams face recurring challenges:

- **Production incidents** require searching old incidents, root causes, resolutions, and runbooks.
- **Code reviews** suffer from repeated feedback because team-specific preferences are not remembered.
- **Deployment failures** are difficult to diagnose without connecting deployment history, build failures, and infrastructure changes.

Engineers solve the same problems repeatedly because institutional knowledge is lost.

## Solution

**IncidentIQ** is an AI-powered platform with **three specialized agents** that use **Hindsight** as their persistent memory layer to:

- Remember past incidents, resolutions, and lessons learned
- Recall team coding preferences and architectural standards
- Learn from deployment failures and infrastructure changes
- Improve recommendations with each interaction

### Why Memory Matters

Traditional AI assistants have no memory between sessions. IncidentIQ uses **Hindsight** — a persistent memory engine — to retain and recall engineering experiences. This means:

- **First interaction**: The agent provides generic analysis
- **Second interaction**: The agent recalls previous experience and provides context-aware recommendations
- **Third interaction**: The agent draws from multiple past experiences for even better recommendations

The agents **genuinely learn and improve over time**, not through fine-tuning, but through persistent experiential memory.

---

## Three Agents

### 🚨 Incident Response Agent
Analyzes production incidents by recalling similar past incidents, root causes, and resolutions from Hindsight memory.

### 🔍 Code Review Agent
Reviews code using team-specific preferences remembered from previous reviews. Clearly separates general best practices from remembered team standards.

### 🚀 DevOps Pipeline Agent
Diagnoses deployment and pipeline failures using historical deployment memories, infrastructure changes, and past resolution patterns.

---

## Architecture

```
USER INPUT
    │
    ▼
  AGENT
    │
    ▼
HINDSIGHT RECALL → Relevant Past Memories
    │
    ▼
CURRENT INPUT + PAST EXPERIENCE
    │
    ▼
  GROQ LLM
    │
    ▼
AI RECOMMENDATION
    │
    ▼
USER SEES RESULT
    │
    ▼
RESOLUTION / OUTCOME
    │
    ▼
HINDSIGHT RETAIN → New Memory
    │
    ▼
FUTURE IMPROVEMENT
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Persistent Memory** | Hindsight (by Vectorize.io) |
| **LLM Reasoning** | Groq |
| **Frontend** | Streamlit |
| **Language** | Python 3.10+ |
| **Configuration** | python-dotenv |

---

## Hindsight Integration

Hindsight is **not** just a database. It is the **central agent memory layer**.

- **Retain**: Store engineering experiences (incidents, reviews, deployments)
- **Recall**: Semantically search for relevant past experiences
- **Reflect**: Synthesize memories into insights (optional)

All three agents share one Hindsight memory bank (`IncidentIQ Memory`) with agent-type metadata to isolate memories per agent.

---

## Memory Flow

1. User submits a problem (incident / code / deployment)
2. Agent queries Hindsight for relevant past experiences
3. Retrieved memories are included in the LLM prompt
4. Groq generates a context-aware recommendation
5. User resolves the issue and provides outcome
6. The complete experience is stored back in Hindsight
7. Future queries benefit from this new memory

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Hindsight API key (from [Vectorize.io](https://hindsight.vectorize.io))
- Groq API key (from [Groq Console](https://console.groq.com))

### 1. Clone the Repository
```bash
git clone <repository-url>
cd IncidentIQ
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in your API keys:
```bash
copy .env.example .env
```

Edit `.env`:
```
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=IncidentIQ Memory

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model

APP_NAME=IncidentIQ
APP_ENV=development
```

> **IMPORTANT**: Never commit your `.env` file. It is listed in `.gitignore`.

### 5. Run Validation Tests
```bash
python test_hindsight.py
```

### 6. Start the Application
```bash
python -m streamlit run app.py
```

Or on Windows:
```bash
run.bat
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HINDSIGHT_API_KEY` | Hindsight API key | Yes |
| `HINDSIGHT_BASE_URL` | Hindsight API URL | Yes |
| `HINDSIGHT_BANK_ID` | Hindsight memory bank name | Yes |
| `GROQ_API_KEY` | Groq API key | Yes |
| `GROQ_MODEL` | Groq model name | Yes |
| `APP_NAME` | Application name | No |
| `APP_ENV` | Environment (development/production) | No |

---

## Demo Workflow

1. Start the application
2. Click **"Load Demo Memories"** in the sidebar to load sample engineering experiences
3. Go to **Incident Response** tab and enter a Payment API incident
4. See Hindsight recall similar past incidents
5. Resolve the incident and store the new experience
6. Submit a similar incident and see improved recommendations
7. Try **Code Review** and **DevOps Pipeline** agents similarly

---

## Project Structure

```
IncidentIQ/
├── app.py                         # Streamlit UI
├── agents/
│   ├── incident_agent.py           # Incident response prompts/logic
│   ├── code_review_agent.py        # Code review prompts/logic
│   └── pipeline_agent.py           # Pipeline prompts/logic
├── memory/
│   └── hindsight_memory.py         # Hindsight SDK wrapper
├── llm/
│   └── groq_client.py              # Groq SDK wrapper
├── services/
│   ├── incident_service.py         # Incident workflow orchestration
│   ├── code_review_service.py      # Code review workflow orchestration
│   └── pipeline_service.py         # Pipeline workflow orchestration
├── utils/
│   ├── config.py                   # Configuration management
│   └── formatting.py               # UI formatting utilities
├── demo/
│   └── demo_memories.py            # Synthetic demo data
├── test_hindsight.py               # Validation tests
├── requirements.txt
├── .env.example
├── .gitignore
├── run.bat
├── README.md
└── DEMO_SCRIPT.md
```

---

## Future Improvements

- Multi-team memory isolation with separate Hindsight banks
- Integration with Slack/PagerDuty for real-time incident ingestion
- GitHub/GitLab webhook integration for automatic code review
- CI/CD pipeline integration for automatic deployment monitoring
- Memory analytics dashboard showing learning trends
- Memory pruning and relevance scoring
- Role-based access control

---

## License

Built for hackathon demonstration purposes.
