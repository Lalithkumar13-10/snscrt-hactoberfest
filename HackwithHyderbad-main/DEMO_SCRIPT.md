# IncidentIQ — Hackathon Demo Script

**Duration: 3–5 minutes**

---

## Opening (30 seconds)

> "Meet IncidentIQ — Engineering agents that remember, learn, and improve."
>
> "Every engineering team faces the same problem: institutional knowledge is lost.
> When a production incident happens at 2 AM, the engineer who solved it last time
> might not be available. Code review feedback is repeated sprint after sprint.
> Deployment failures are diagnosed from scratch every time."
>
> "IncidentIQ solves this with three AI agents backed by Hindsight —
> a persistent memory layer that lets agents genuinely learn from experience."

---

## Demo Step 1: Show the Platform (15 seconds)

1. Show the IncidentIQ interface
2. Point out the **three agent tabs**: Incident Response, Code Review, DevOps Pipeline
3. Show the **System Status** sidebar: Hindsight Connected, Groq Connected, Memory Bank

---

## Demo Step 2: Load Demo Data (15 seconds)

1. Click **"Load Demo Memories"** in the sidebar
2. Show the confirmation: "12 demo memories loaded"
3. Explain: "These represent past engineering experiences — incidents, code reviews, deployments"

---

## Demo Step 3: Incident Response — The Learning Loop (90 seconds)

### First Incident
1. Go to **Incident Response** tab
2. Enter:
   - Incident ID: `INC-NEW-001`
   - Service: `Payment API`
   - Severity: `Critical`
   - Environment: `AWS Production`
   - Error: `HTTP 500 — Database connection timeout`
   - Description: `Payment API returning 500 errors. Users unable to complete purchases. Database connections appear to be timing out.`
3. Click **"Analyze Incident"**
4. **Show the Hindsight Memory section**:
   > "Look — Hindsight found previous incidents with similar patterns.
   > INC-001 had a connection pool exhaustion issue.
   > INC-004 had database timeout from batch processing."
5. **Show the AI Analysis**:
   > "The agent uses these past experiences to recommend specific actions —
   > not generic troubleshooting, but actions based on what actually worked before."
6. **Show Memory Influence**:
   > "The UI clearly shows which memories influenced this recommendation."

### Resolve and Learn
7. Click **"Mark Resolved & Learn"**
8. Enter:
   - Root Cause: `Database connection pool exhausted during flash sale traffic spike`
   - Resolution: `Increased connection pool from 100 to 200 and added auto-scaling`
   - Outcome: `Service recovered in 8 minutes`
   - Lesson: `Implement connection pool auto-scaling for traffic spikes`
9. Click **"Save & Learn"**
10. > "This experience is now stored in Hindsight. Next time a similar incident occurs,
    > the agent will recall this resolution too."

---

## Demo Step 4: Code Review — Team Preferences (45 seconds)

1. Go to **Code Review** tab
2. Enter:
   - Repository: `payment-api`
   - Language: `Python`
   - Code:
     ```python
     def process_payment(user_id, amount):
         db = get_connection()
         result = db.execute("SELECT * FROM users WHERE id = " + str(user_id))
         user = result.fetchone()
         db.execute(f"INSERT INTO payments (user_id, amount) VALUES ({user_id}, {amount})")
         db.commit()
         return {"status": "ok"}
     ```
3. Click **"Review Code"**
4. **Show team preferences from memory**:
   > "Notice: the agent recalls that this team prefers the Repository Pattern
   > and avoids raw SQL in service classes. These aren't generic rules —
   > they come from actual past review feedback stored in Hindsight."
5. **Show the distinction**:
   > "Critical issues like SQL injection are GENERAL PRACTICES.
   > But 'use Repository Pattern' is a REMEMBERED TEAM PREFERENCE."

---

## Demo Step 5: DevOps Pipeline — Historical Matching (30 seconds)

1. Go to **DevOps Pipeline** tab
2. Enter:
   - Pipeline ID: `DEP-NEW-001`
   - Service: `Order Service`
   - Version: `v2.5.0`
   - Environment: `AWS Production`
   - Build: `Passed`
   - Deployment: `Failed`
   - Error: `Redis connection timeout after deployment`
3. Click **"Analyze Pipeline"**
4. > "The agent recalls DEP-001 — a previous Order Service deployment that also
   > failed with Redis timeout. That time, it was a Terraform security group change.
   > The agent recommends investigating the same area."

---

## Demo Step 6: Learning Timeline (15 seconds)

1. Show the **Learning Timeline** section in the sidebar
2. > "This timeline shows how the agent improves over time.
   > First interaction: no memory, generic response.
   > Second interaction: recalls past experience, better recommendations.
   > Third interaction: multiple memories, most context-aware analysis."

---

## Closing (30 seconds)

> "What makes IncidentIQ different from a regular AI chatbot?"
>
> "It remembers. It learns. It improves."
>
> "Hindsight is not just a database — it's a memory engine that lets agents
> retain experiences, recall relevant context, and provide increasingly
> better recommendations with each interaction."
>
> "Every resolved incident, every code review, every deployment outcome
> becomes part of the team's collective AI memory."
>
> "Thank you. Questions?"

---

## Quick Reference — Demo Data Available

| Agent | Demo Memories |
|-------|---------------|
| Incident Response | 4 incidents (Payment API x2, Auth Service, Order Service) |
| Code Review | 4 team preferences (Repository Pattern, No Raw SQL, Exception Handling, Service/Repo Separation) |
| DevOps Pipeline | 4 deployments (Redis timeout, Env var mismatch, K8s OOM, DB migration failure) |
