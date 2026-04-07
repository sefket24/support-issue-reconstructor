# 🔍 Reducing Ambiguity in Complex Support Workflows

> AI-powered issue triage and response drafting for SaaS support teams — built with Python, Streamlit, and OpenAI.

**Live demo:** [support-issue-reconstructor.streamlit.app](https://support-issue-reconstructor.streamlit.app/)

---

## Context

Modern SaaS products increasingly involve:

- Multiple users interacting with shared resources
- Layered abstractions (components, automations, integrations)
- Asynchronous changes across systems

These environments make issues difficult to reproduce, attribute, and explain clearly. A single inbound ticket might touch three different subsystems, involve two user roles, and arrive with just enough detail to be confusing — but not enough to act on.

---

## Problem

Support teams processing high volumes of complex, ambiguous tickets face a consistent set of challenges. Manually reviewing each one is:

- Time-consuming for support agents
- Inconsistent across team members
- Hard to scale as request volume grows

---

## Solution

This tool provides an AI-powered first-pass review. An agent pastes an incoming ticket (or fills out the intake form), and the assistant instantly returns:

- A **classification** (Actionable / Needs Clarification / Out of Scope)
- A **reasoning summary** explaining the decision
- A **tone analysis** of the reporter
- A **suggested reply** ready to copy and send
- **Tags** for categorization and routing

This frees support agents to focus on edge cases, exceptions, and relationship-building — not repetitive triage.

---

## How It Works

1. The support agent fills in the intake form:
   - Product area or context
   - Reporter email
   - Free-text description of the issue
   - Checkbox confirming supporting evidence has been provided

2. On submission, a structured prompt is sent to the OpenAI API (`gpt-4o-mini`).

3. The model returns a JSON object with classification, reasoning, tone, suggested response, and tags.

4. Results are displayed in a clean side-by-side layout with color-coded status badges.

---

## Example Input / Output

**Input:**
- Context: `Collaborative canvas tool, 12-seat team`
- Email: `ops@examplecorp.com`
- Message: *"One of our users says changes they made aren't showing up for others on the team. It was working yesterday. We haven't changed any settings."*
- Evidence provided: ✅ Yes (screen recording attached)

**Output:**
```json
{
  "classification": "needs_clarification",
  "reasoning": "The issue likely involves a sync or permission layer, but the ticket lacks detail on which feature area, user role affected, and whether the problem is consistent or intermittent. A targeted follow-up will accelerate resolution.",
  "tone": "Calm but concerned — reporting on behalf of another user",
  "suggested_response": "Thanks for reaching out and for attaching the recording — that's helpful. To investigate further, could you confirm which canvas feature this affects and whether the issue is happening for all team members or just one? Once we have that, we can identify whether this is a sync, permission, or session issue and get it resolved quickly.",
  "tags": ["sync-issue", "multi-user", "needs-repro-steps", "collaborative-feature"]
}
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/sefket24/support-issue-reconstructor.git
cd support-issue-reconstructor
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder with your real key:

```
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Deploy on Streamlit Cloud

1. Push your repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app** → connect your GitHub account
4. Select your repo and set `app.py` as the main file
5. Under **Advanced settings → Secrets**, add:

```
OPENAI_API_KEY = "sk-...your-key-here..."
```

6. Click **Deploy**

---

## Tech Stack

| Layer | Tool |
|-------|------|
| UI | Streamlit |
| AI | OpenAI GPT-4o-mini + GPT-4o vision |
| Config | python-dotenv |
| Language | Python 3.10+ |

---

## Inspiration

This project was inspired by the challenge of processing high-volume, hard-to-reproduce support tickets in complex collaborative SaaS environments. It demonstrates how a focused AI integration can meaningfully reduce manual review time, surface the right follow-up questions faster, and improve response quality at scale.

---

## License

MIT — free to use, modify, and build on.
