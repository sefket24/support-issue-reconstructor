# Support Issue Reconstructor
## Reducing Ambiguity in Complex Support Workflows

---

## Problem

Modern SaaS products are multi-actor environments. Users, admins, automations, and background sync processes all interact with the same data — often within seconds of each other. When something breaks, it rarely leaves an obvious trace.

The result is a support workflow that looks like this:

- User reports something changed that shouldn't have, or something didn't happen that should have
- Support asks for screenshots, timestamps, and steps to reproduce
- User can't always answer those questions — they just noticed it was wrong
- Support escalates to engineering or checks the database directly
- 3–5 messages later, you find out an automation condition was updated by a teammate two hours before the issue started

That back-and-forth is the problem. Not every case is simple enough to resolve in one message, but many are — if you could quickly reconstruct *what actually happened* before asking the user anything.

---

## Observations

After handling a large volume of complex support tickets, several patterns emerged:

**Multi-actor collisions.** Issues frequently involve more than one actor — a user makes a change, a background process runs shortly after, and the user sees the combined result as unexpected behavior. Neither action is wrong in isolation.

**Silent automation and sync failures.** Automations don't always throw errors when they stop working. A trigger condition mismatch causes a silent skip. A sync job overwrites a manual edit without surfacing a conflict. The user sees a wrong value with no error message to point to.

**Hard to identify what changed and when.** Even when an audit log exists, reading it to reconstruct a sequence of events requires time and context. A support engineer dealing with 40 tickets a day doesn't have either.

**Reproducibility is low.** Because these issues involve specific timing, specific actors, and specific configurations, they're hard to reproduce intentionally — which makes root cause harder to confirm.

---

## Hypothesis

If we can reconstruct the likely sequence of events — even imperfectly — at the start of an investigation, we reduce the number of clarifying questions needed and get to a fix faster.

A structured reconstruction, even if it's 70–80% accurate, is more useful than 3 rounds of back-and-forth, because it gives the support engineer and the user something concrete to confirm or correct. The conversation shifts from "can you describe what happened?" to "does this match what you saw?"

---

## Proposed Solution

**Support Issue Reconstructor** is a lightweight internal tool that takes an issue description and an optional event log and produces:

- A reconstructed event timeline showing what likely happened and in what order
- A root cause explanation written in plain support language
- A list of contributing factors — the conditions that made the issue possible
- Actionable suggested fixes, ordered by specificity
- Numbered reproduction steps that can be handed off to QA or engineering

The tool is not trying to replace judgment. It's trying to give the support engineer a starting point — a structured hypothesis that can be confirmed, refined, or dismissed quickly.

The analysis engine is deterministic and rule-based. It doesn't call an LLM. It uses a knowledge base built from real support patterns, mapped to issue categories. This makes it fast, auditable, and usable without any API keys or internet access.

---

## Example Scenario

### Incoming ticket

> "Our approval automation stopped running. Nothing changed on our end. It was working last week."

**Before this tool:**

1. Support asks for the automation name and which records it's supposed to act on
2. User shares the automation — support checks the trigger conditions
3. Support asks when it last worked
4. User isn't sure
5. Support checks the audit log and finds a teammate edited the automation 3 days ago
6. Support identifies the trigger condition change — a new filter was added that most records don't satisfy

Resolution: 5 messages, 1–2 days elapsed.

**After this tool:**

1. Support pastes the issue description, selects "automation / workflow", generates a mock or uploads an event log
2. Tool surfaces: `automation_config_updated` as the most suspicious event, explains that a trigger condition change could cause silent skips, and lists "check whether records satisfy all current trigger conditions" as the first fix
3. Support goes directly to the automation audit log with a clear hypothesis
4. Confirms the change, identifies the affected records, resolves

Resolution: 1 message, same session.

---

## Expected Impact

- Faster time-to-first-useful-response on ambiguous tickets
- Fewer clarifying questions needed from the user in the initial triage phase
- Support engineers spend less time reading raw audit logs from scratch
- Reproducible cases are documented in a standard format that engineering can act on
- Institutional knowledge about common failure patterns is captured in the tool rather than individual engineers' heads

---

## Assumptions & Reasoning

**Assumption:** Most complex support issues fall into a small number of recognizable categories — data inconsistency, permission changes, automation failures, sync/state conflicts.

**Reasoning:** After handling a large volume of tickets, the same patterns recur. The specifics change but the structure doesn't. A rule-based engine trained on those patterns can get close enough to be useful without needing an LLM.

**Assumption:** A partial reconstruction is more useful than no reconstruction.

**Reasoning:** Even if the tool is only 70–80% accurate, it gives the support engineer a direction to look. That's faster than starting from scratch.

**Assumption:** Support engineers will use it if it's fast and doesn't require setup.

**Reasoning:** A tool that requires an API key, a database connection, or a lot of manual input won't get used in a high-volume support environment. This tool runs locally with no external dependencies and produces output in under a second.

---

## Validation Plan

1. **Pilot with known cases.** Run the tool against 10–15 resolved tickets where the root cause is already confirmed. Measure how close the tool's output is to the actual cause.

2. **Track time-to-resolution on new tickets.** Compare resolution time for tickets where the tool was used vs. tickets handled without it.

3. **Collect support engineer feedback.** After each use, ask: was the reconstruction useful? Did it point in the right direction? What was missing?

4. **Iterate on the knowledge base.** As new patterns emerge, add them to the analyzer. The tool gets more accurate over time without requiring a model retrain.

---

## Demo Instructions

### Run locally

```bash
# Clone the repo
git clone https://github.com/your-username/support-issue-reconstructor.git
cd support-issue-reconstructor

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

**To test with a real event log:** Upload any JSON array of event objects using the file uploader. Each event should have `timestamp`, `actor`, `action`, and `detail` fields. See `/data/mock_events.json` for the expected format.

**To test without an event log:** Leave the checkbox enabled — the tool will generate a realistic mock event log based on the issue category you selected.

### Sample cases

Pre-built test cases are available in `/examples/sample_cases.json`. Each case includes a realistic issue description, a structured event log, and the expected output for validation.

---

### Live Demo

This app is deployed via Streamlit Community Cloud.

👉 [https://support-issue-reconstructor.streamlit.app](https://support-issue-reconstructor.streamlit.app)

---

## Notes

This project is based on common patterns observed in complex SaaS support environments. A more tailored version — with category definitions, event types, and knowledge base entries specific to your product — can be shared upon request.

The knowledge base lives in `logic/analyzer.py` and `logic/classifier.py`. Both files are structured to make it straightforward to add new categories, event types, and fix suggestions without touching the rest of the codebase.
