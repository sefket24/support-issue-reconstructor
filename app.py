import streamlit as st

st.set_page_config(page_title="Support Issue Reconstructor")

st.markdown("""
### 👋 Hey, hiring team!

This is a portfolio project by Sef Nouri — a working support tool that simulates how SaaS teams translate messy user issues into structured, reproducible bug reports for engineering.

Feel free to test it with a real support message.

[⌥ GitHub](https://github.com/sefket24/support-issue-reconstructor)  
[🔗 LinkedIn](https://www.linkedin.com/)
""")

st.markdown("""---""")

st.markdown("""
### 🤝 Support Issue Reconstructor  
**Product Support · Internal Tool · Issue Reproduction**
""")

st.title("Support Issue Reconstructor")

st.markdown(
"""
Paste a real user message below.  
This tool translates unclear support tickets into structured, reproducible issues for engineering.
"""
)

# Intake
st.header("1. User Issue")

user_issue = st.text_area("User message (raw)", placeholder="Paste the user's message here...")

col1, col2 = st.columns(2)

with col1:
    browser = st.text_input("Browser (required)")

with col2:
    os = st.text_input("Operating System (required)")

auth = st.selectbox("Auth State", ["Select...", "Logged in", "Logged out", "Unknown"])
frequency = st.selectbox("Frequency", ["Select...", "Always", "Intermittent", "Once"])

# Investigation
st.header("2. Investigation")

hypothesis = st.text_area("What do you suspect?")
steps_taken = st.text_area("What have you tried?")

# Output
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
