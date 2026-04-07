import streamlit as st

st.set_page_config(page_title="Support Issue Reconstructor", layout="wide")

# Header
st.markdown("""
<div style="background:#0f172a;padding:16px 20px;border-radius:10px;color:white;">
<b>Support Issue Reconstructor</b>
<span style="float:right;font-size:12px;opacity:0.7;">Product Support | Internal Tool</span>
</div>
""", unsafe_allow_html=True)

# Banner
st.markdown("""
<div style="background:#fef3c7;padding:14px;border-radius:8px;margin-top:12px;">
<b>Hey, hiring team!</b> This simulates how SaaS support turns messy user issues into structured bug reports.
<br><br>
<a href="https://github.com/sefket24/support-issue-reconstructor" target="_blank">GitHub</a> | 
<a href="https://www.linkedin.com/in/sefketnouri/" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)

st.markdown("### Try it")

# Sample autofill
if st.button("Try a sample issue"):
    st.session_state["user_issue"] = "Users report a blank screen when opening shared link"
    st.session_state["browser"] = "Chrome"
    st.session_state["os"] = "macOS"
    st.session_state["auth"] = "Logged out"
    st.session_state["frequency"] = "Always"

# Inputs
user_issue = st.text_area("User issue", key="user_issue")

col1, col2 = st.columns(2)
browser = col1.text_input("Browser", key="browser")
os = col2.text_input("OS", key="os")

auth = st.selectbox("Auth", ["Logged in","Logged out","Unknown"], key="auth")
frequency = st.selectbox("Frequency", ["Always","Intermittent","Once"], key="frequency")

hypothesis = st.text_area("Hypothesis")
steps = st.text_area("Steps tried")

# Output
if st.button("Generate"):
    if not user_issue or not browser or not os:
        st.error("Fill required fields")
    else:
        st.markdown("## Ticket Output")

        st.markdown(f'''
<div style="border:1px solid #e5e7eb;padding:16px;border-radius:10px;background:white;">

<b>Steps to Reproduce</b>
<ul>
<li>Open link</li>
<li>Observe issue</li>
</ul>

<b>Expected</b>
<p>Feature works normally</p>

<b>Actual</b>
<p>Issue occurs</p>

<b>Environment</b>
<p>{browser} | {os} | {auth}</p>

<b>Notes</b>
<p>{hypothesis}</p>

</div>
''', unsafe_allow_html=True)
