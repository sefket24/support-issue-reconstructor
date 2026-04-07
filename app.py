import streamlit as st

st.set_page_config(page_title="Support Issue Reconstructor")

# --- Top Header ---
st.markdown("""
<div style="
    background-color: #0f172a;
    padding: 20px 24px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 20px; font-weight: 600;">
            🤝 Support Issue Reconstructor
        </div>
        <div style="font-size: 12px; opacity: 0.7;">
            Product Support · Internal Tool
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Banner Card ---
st.markdown("""
<div style="
    background-color: #fef9c3;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #fde68a;
    margin-bottom: 25px;
">
    <div style="font-size: 14px;">
        👋 <strong>Hey, hiring team!</strong> This is a portfolio project by <strong>Sef Nouri</strong> — a working support tool that simulates how SaaS teams turn messy user issues into structured, reproducible bug reports for engineering.
        <br><br>
        Feel free to test it with a real support message.
    </div>

    <div style="margin-top: 12px;">
        <a href="https://github.com/sefket24/support-issue-reconstructor" target="_blank"
            style="text-decoration: none; margin-right: 10px;">
            <button style="
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #cbd5e1;
                background-color: white;
                cursor: pointer;
            ">
                ⌥ GitHub
            </button>
        </a>

        <a href="https://www.linkedin.com/in/sefketnouri/" target="_blank"
            style="text-decoration: none;">
            <button style="
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #cbd5e1;
                background-color: white;
                cursor: pointer;
            ">
                in LinkedIn
            </button>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
"""
Paste a real user message below.  
This tool translates unclear support tickets into structured, reproducible issues for engineering.
"""
)

# --- Intake ---
st.header("1. User Issue")

user_issue = st.text_area("User message (raw)", placeholder="Paste the user's message here...")

col1, col2 = st.columns(2)

with col1:
    browser = st.text_input("Browser (required)")

with col2:
    os = st.text_input("Operating System (required)")

auth = st.selectbox("Auth State", ["Select...", "Logged in", "Logged out", "Unknown"])
frequency = st.selectbox("Frequency", ["Select...", "Always", "Intermittent", "Once"])

# --- Investigation ---
st.header("2. Investigation")

hypothesis = st.text_area("What do you suspect?")
steps_taken = st.text_area("What have you tried?")

# --- Output ---
st.header("3. Structured Output")

if st.button("Generate Report"):
    if not user_issue or not browser or not os or auth == "Select..." or frequency == "Select...":
        st.error("Fill in all required fields before generating the report.")
    else:
        report = f"""
STEPS TO REPRODUCE
1. ...
2. ...

EXPECTED
...

ACTUAL
...

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
        st.download_button("Download Report", report, file_name="support_issue.txt")
