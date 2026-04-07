import streamlit as st

st.set_page_config(page_title="Support Issue Reconstructor")

st.title("I turn vague user issues into structured, reproducible bugs")

st.markdown(
"""
Built from real support workflows.

Paste a real user message below. This tool helps translate unclear tickets into structured, actionable issues for engineering.
"""
)

# --- Intake ---
st.header("1. User Issue")

user_issue = st.text_area("User message (raw)", placeholder="Paste the user's message here...")

col1, col2 = st.columns(2)

with col1:
    browser = st.text_input("Browser (required)", placeholder="e.g. Chrome, Safari")

with col2:
    os = st.text_input("Operating System (required)", placeholder="e.g. macOS, Windows")

auth = st.selectbox("Auth State", ["Select...", "Logged in", "Logged out", "Unknown"])

frequency = st.selectbox("Frequency", ["Select...", "Always", "Intermittent", "Once"])

# --- Investigation ---
st.header("2. Investigation")

hypothesis = st.text_area("What do you suspect is happening?", placeholder="Permissions? Caching? Browser issue?")

steps_taken = st.text_area("What have you already tried?", placeholder="Reproduced in incognito, checked permissions, etc.")

# --- Output ---
st.header("3. Structured Output")

if st.button("Generate Report"):
    if not user_issue or not browser or not os or auth == "Select..." or frequency == "Select...":
        st.error("Fill in all required fields before generating the report.")
    else:
        report = f"""
STEPS TO REPRODUCE
1. [Based on investigation]
2. [Add steps]

EXPECTED
[What should happen]

ACTUAL
[What is happening]

ENVIRONMENT
Browser: {browser}
OS: {os}
Auth: {auth}
Frequency: {frequency}

NOTES FOR ENGINEERING
User issue: {user_issue}

Hypothesis:
{hypothesis}

Steps taken:
{steps_taken}
"""

        st.code(report)

        st.markdown("This is what I would send to engineering after investigating a ticket.")

        st.download_button(
            "Download Report",
            report,
            file_name="support_issue.txt"
        )
