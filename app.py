import streamlit as st
import json
import os
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Support Issue Reconstructor",
    page_icon="🔍",
    layout="wide",
)

# ── Session state for stats ───────────────────────────────────────────────────
if "total_requests" not in st.session_state:
    st.session_state.total_requests = 0
if "actionable_count" not in st.session_state:
    st.session_state.actionable_count = 0
if "last_process_time" not in st.session_state:
    st.session_state.last_process_time = None

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        color: #1a1a1a;
    }
    .stApp {
        background-color: #f4f3ef !important;
    }
    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1140px;
    }

    /* ── Top nav bar ── */
    .nav-bar {
        background: #111;
        border-radius: 12px;
        padding: 1rem 1.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.25rem;
    }
    .nav-brand {
        display: flex; align-items: center; gap: 0.75rem;
    }
    .nav-brand h1 {
        color: #f4f3ef; margin: 0;
        font-size: 1.1rem; font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
    }
    .nav-badge {
        background: #c8f55a; color: #111;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem; font-weight: 700;
        padding: 2px 7px; border-radius: 3px;
        letter-spacing: 1.5px; text-transform: uppercase;
    }
    .nav-meta {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem; color: #666;
    }

    /* ── Portfolio banner ── */
    .portfolio-banner {
        background: #fffdf0;
        border: 1px solid #f0e68c;
        border-left: 4px solid #c8f55a;
        border-radius: 8px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    .portfolio-banner-text {
        font-size: 0.85rem;
        color: #444;
        line-height: 1.5;
    }
    .portfolio-banner-text strong {
        color: #111;
        font-weight: 600;
    }
    .portfolio-links {
        display: flex;
        gap: 0.6rem;
        white-space: nowrap;
    }
    .portfolio-link {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 5px;
        text-decoration: none;
        border: 1px solid #d4d0c8;
        color: #333;
        background: #fff;
    }
    .portfolio-link:hover { background: #111; color: #c8f55a; border-color: #111; }

    /* ── Stat cards ── */
    .stats-row {
        display: flex; gap: 1rem; margin-bottom: 1.25rem;
    }
    .stat-card {
        flex: 1;
        background: #fff;
        border: 1px solid #e0ddd6;
        border-radius: 10px;
        padding: 1rem 1.25rem;
    }
    .stat-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem; font-weight: 600;
        color: #999; text-transform: uppercase;
        letter-spacing: 1px; margin-bottom: 0.3rem;
    }
    .stat-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.6rem; font-weight: 600; color: #111;
        line-height: 1;
    }
    .stat-sub {
        font-size: 0.75rem; color: #aaa; margin-top: 0.2rem;
    }

    /* ── Cards ── */
    .form-card {
        background: #fff;
        border: 1px solid #e0ddd6;
        border-radius: 12px;
        padding: 1.6rem;
    }
    .result-card {
        background: #fff;
        border: 1px solid #e0ddd6;
        border-radius: 12px;
        padding: 1.6rem;
    }

    /* ── Progress steps ── */
    .step-row {
        display: flex; gap: 0.5rem;
        margin-bottom: 1.25rem;
    }
    .step {
        flex: 1; padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem; font-weight: 600;
        text-align: center;
    }
    .step-pending { background: #f4f3ef; color: #bbb; border: 1px solid #e0ddd6; }
    .step-active  { background: #111; color: #c8f55a; border: 1px solid #111; }
    .step-done    { background: #d4f7d4; color: #1a6b1a; border: 1px solid #a8e6a8; }
    .step-error   { background: #fde8e8; color: #8b1a1a; border: 1px solid #f0a8a8; }

    /* ── Doc result ── */
    .doc-verified   { background:#d4f7d4; border:1px solid #a8e6a8; border-radius:8px; padding:0.6rem 1rem; font-size:0.82rem; color:#1a6b1a; font-family:'IBM Plex Mono',monospace; margin-bottom:1rem; }
    .doc-unverified { background:#fff7d4; border:1px solid #f0d890; border-radius:8px; padding:0.6rem 1rem; font-size:0.82rem; color:#7a5c00; font-family:'IBM Plex Mono',monospace; margin-bottom:1rem; }

    /* ── Status badges ── */
    .status-actionable   { display:inline-block; background:#d4f7d4; color:#1a6b1a; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #a8e6a8; }
    .status-needs-review { display:inline-block; background:#fff7d4; color:#7a5c00; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #f0d890; }
    .status-out-of-scope { display:inline-block; background:#fde8e8; color:#8b1a1a; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #f0a8a8; }

    /* ── Confidence bar ── */
    .confidence-wrap { margin: 0.75rem 0 1rem; }
    .confidence-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem; color: #888;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .confidence-track {
        background: #f0efe9; border-radius: 99px;
        height: 8px; width: 100%; overflow: hidden;
    }
    .confidence-fill {
        height: 100%; border-radius: 99px;
        transition: width 0.4s ease;
    }
    .conf-high   { background: #4caf50; }
    .conf-medium { background: #ff9800; }
    .conf-low    { background: #f44336; }
    .confidence-pct {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem; color: #555;
        margin-top: 0.25rem;
    }

    /* ── Risk flags ── */
    .risk-flag {
        display: inline-block;
        background: #fff3e0; color: #e65100;
        border: 1px solid #ffcc80;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem; padding: 3px 9px;
        border-radius: 4px; margin: 2px 3px 2px 0;
    }

    /* ── Section label ── */
    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem; font-weight: 600; color: #999;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 0.3rem; margin-top: 1rem;
    }

    /* ── Response box ── */
    .response-box {
        background: #f4f3ef;
        border-left: 4px solid #111;
        border-radius: 0 8px 8px 0;
        padding: 1.1rem 1.4rem;
        font-size: 0.88rem; line-height: 1.75;
        color: #333; white-space: pre-wrap;
    }

    /* ── Tags ── */
    .tag { display:inline-block; background:#111; color:#f4f3ef; font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:3px 9px; border-radius:4px; margin:2px 3px 2px 0; }

    /* ── Process time ── */
    .process-time {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem; color: #bbb;
        text-align: right; margin-top: 1rem;
    }

    /* ── Placeholder ── */
    .result-placeholder {
        background: #f4f3ef; border: 2px dashed #d4d0c8;
        border-radius: 8px; padding: 3rem 2rem;
        text-align: center; color: #bbb;
        font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem;
    }

    /* ── Streamlit overrides ── */
    .stButton > button {
        background: #111 !important; color: #f4f3ef !important;
        border: none !important; border-radius: 8px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important; font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important; width: 100% !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover { background: #333 !important; color: #c8f55a !important; }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #d4d0c8 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.9rem !important;
        background: #fafaf8 !important;
        color: #1a1a1a !important;
    }
    .stCheckbox > label { font-size: 0.88rem; color: #444; }

    div[data-testid="stFileUploader"] {
        border: 2px dashed #d4d0c8 !important;
        border-radius: 8px !important;
        background: #fafaf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Nav bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <div class="nav-brand">
        <span style="font-size:1.3rem">🔍</span>
        <h1>Support Issue Reconstructor</h1>
        <span class="nav-badge">AI-Powered</span>
    </div>
    <div class="nav-meta">Support Ops · Internal Tool</div>
</div>
""", unsafe_allow_html=True)


# ── Portfolio banner ──────────────────────────────────────────────────────────
st.markdown("""
<div class="portfolio-banner">
    <div class="portfolio-banner-text">
        👋 <strong>Hey, hiring team!</strong> This is a portfolio project by <strong>Sef Nouri</strong> —
        a working AI app that simulates how SaaS support teams could reduce ambiguity in complex,
        hard-to-reproduce support tickets using LLM-based triage, tone analysis, and response drafting.
        Feel free to test it with a real request.
    </div>
    <div class="portfolio-links">
        <a class="portfolio-link" href="https://github.com/sefket24/support-issue-reconstructor" target="_blank">⌥ GitHub</a>
        <a class="portfolio-link" href="https://www.linkedin.com/in/sefketnouri" target="_blank">in LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Stats row ─────────────────────────────────────────────────────────────────
total      = st.session_state.total_requests
actionable = st.session_state.actionable_count
rate       = f"{int(actionable/total*100)}%" if total > 0 else "—"
proc_t     = f"{st.session_state.last_process_time:.1f}s" if st.session_state.last_process_time else "—"

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">Tickets Processed</div>
        <div class="stat-value">{total}</div>
        <div class="stat-sub">this session</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Actionable Rate</div>
        <div class="stat-value">{rate}</div>
        <div class="stat-sub">clear next-step classifications</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Avg Process Time</div>
        <div class="stat-value">{proc_t}</div>
        <div class="stat-sub">last request</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">AI Models</div>
        <div class="stat-value" style="font-size:0.95rem;padding-top:0.2rem">GPT-4o<br>GPT-4o-mini</div>
        <div class="stat-sub">vision + analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_file(uploaded_file):
    raw = uploaded_file.read()
    return base64.b64encode(raw).decode("utf-8"), uploaded_file.type or "application/octet-stream"


def verify_document(client, b64, mime):
    if mime == "application/pdf":
        content = [
            {"type": "text", "text": (
                "This document was uploaded as supporting evidence for a support ticket. "
                "Does it appear to be a legitimate document relevant to a SaaS support issue "
                "(e.g. screenshot, error log, configuration export)? "
                "Reply ONLY with JSON: {\"verified\": true/false, \"doc_summary\": \"one sentence\"}"
            )},
            {"type": "document", "source": {"type": "base64", "media_type": mime, "data": b64}}
        ]
    else:
        content = [
            {"type": "text", "text": (
                "This image was uploaded as supporting evidence for a support ticket. "
                "Does it appear to be a legitimate document relevant to a SaaS support issue "
                "(e.g. screenshot, error log, configuration export)? "
                "Reply ONLY with JSON: {\"verified\": true/false, \"doc_summary\": \"one sentence\"}"
            )},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
        ]

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=200, temperature=0,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())


def analyze_request(product_area, email, message, has_attachment, doc_verified=False, doc_summary=""):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.error("⚠️  OPENAI_API_KEY not found.")
        st.stop()

    client = OpenAI(api_key=api_key)

    doc_context = ""
    if doc_summary:
        status = "VERIFIED" if doc_verified else "UNVERIFIED"
        doc_context = f"\nAttachment: {doc_summary} [{status}]"

    prompt = f"""You are a senior SaaS support agent triaging a complex, potentially hard-to-reproduce support ticket.

Product area / context: {product_area}
Reporter email: {email}
Attachment provided: {has_attachment}{doc_context}

Ticket message:
\"\"\"{message}\"\"\"

Return ONLY a valid JSON object with these exact fields:
{{
  "classification": "actionable" | "needs_clarification" | "out_of_scope",
  "confidence": <integer 0-100>,
  "reasoning": "2-3 sentence explanation of the triage decision",
  "tone": "brief tone description of the reporter",
  "risk_flags": ["flag1", "flag2"],
  "suggested_response": "warm professional reply 3-5 sentences with clear next steps",
  "tags": ["tag1", "tag2", "tag3"]
}}

Rules:
- classification actionable: issue is clear enough to investigate or reproduce immediately
- classification needs_clarification: missing repro steps, unclear scope, multi-user ambiguity, or insufficient context
- classification out_of_scope: feature request, billing issue, or unrelated to the product
- confidence: certainty in the classification (0=very unsure, 100=certain)
- risk_flags: 0-3 specific concerns (e.g. "missing repro steps", "multi-user scope unclear", "async timing issue", "no error message provided", "affects multiple accounts"). Empty list [] if none.
- suggested_response: ask targeted clarifying questions if needs_clarification; provide next steps if actionable
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())


# ── Layout ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Ticket Intake Form")
    st.markdown("---")

    product_area = st.text_input("Product Area / Context", placeholder="e.g. Collaborative canvas, CRM automation, no-code workflow builder")
    email        = st.text_input("Reporter Email", placeholder="e.g. user@company.com")
    message      = st.text_area(
        "Ticket Message",
        placeholder="Paste the support ticket or describe the issue — include any error messages, steps taken, and who is affected...",
        height=150,
    )

    st.markdown("**Supporting Evidence**")
    st.caption("Upload a screenshot, error log, or exported config. Accepts PDF, PNG, JPG.")
    uploaded_doc = st.file_uploader(
        "Upload attachment",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    has_attachment = st.checkbox("✅ Supporting evidence has been attached or is available on request")

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🔍 Reconstruct & Triage Issue")
    st.markdown('</div>', unsafe_allow_html=True)


with right_col:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 Triage Analysis")
    st.markdown("---")

    if not submit:
        st.markdown("""
        <div class="result-placeholder">
            Submit a ticket to see<br>the AI triage analysis here.
        </div>
        """, unsafe_allow_html=True)

    else:
        if not product_area.strip() or not message.strip():
            st.warning("Please fill in Product Area and Ticket Message.")
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                st.error("⚠️  OPENAI_API_KEY not found.")
                st.stop()

            client   = OpenAI(api_key=api_key)
            t_start  = time.time()
            doc_verified = False
            doc_summary  = ""

            # ── Step indicators ──
            has_doc = uploaded_doc is not None
            step1_class = "step-active" if has_doc else "step-pending"
            st.markdown(f"""
            <div class="step-row">
                <div class="step {step1_class}">① Attachment</div>
                <div class="step step-active">② AI Triage</div>
                <div class="step step-pending">③ Complete</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Step 1: attachment verification ──
            if has_doc:
                with st.spinner("🔎 Analysing attachment with GPT-4o vision..."):
                    try:
                        b64, mime    = encode_file(uploaded_doc)
                        doc_result   = verify_document(client, b64, mime)
                        doc_verified = doc_result.get("verified", False)
                        doc_summary  = doc_result.get("doc_summary", "Attachment uploaded")
                    except Exception as e:
                        st.warning(f"Attachment analysis failed: {e}")

                if doc_verified:
                    st.markdown(f'<div class="doc-verified">✅ Attachment recognised — {doc_summary}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="doc-unverified">⚠️ Attachment unclear — {doc_summary}</div>', unsafe_allow_html=True)

            # ── Step 2: triage ──
            with st.spinner("🤖 Triaging issue..."):
                try:
                    result = analyze_request(product_area, email, message, has_attachment, doc_verified, doc_summary)
                except json.JSONDecodeError:
                    st.error("Unexpected AI response format. Please try again.")
                    st.stop()
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.stop()

            t_elapsed = time.time() - t_start
            st.session_state.total_requests += 1
            st.session_state.last_process_time = t_elapsed
            if result.get("classification") == "actionable":
                st.session_state.actionable_count += 1

            # ── Step 3 complete ──
            doc_ok = "step-done" if doc_verified else ("step-error" if has_doc else "step-pending")
            st.markdown(f"""
            <div class="step-row">
                <div class="step {doc_ok}">① Attachment</div>
                <div class="step step-done">② AI Triage</div>
                <div class="step step-done">③ Complete</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Classification + confidence ──
            classification = result.get("classification", "needs_clarification")
            confidence     = result.get("confidence", 50)

            if classification == "actionable":
                badge = '<span class="status-actionable">✅ Actionable</span>'
            elif classification == "out_of_scope":
                badge = '<span class="status-out-of-scope">❌ Out of Scope</span>'
            else:
                badge = '<span class="status-needs-review">⚠️ Needs Clarification</span>'

            st.markdown(badge, unsafe_allow_html=True)

            # Confidence bar
            conf_class = "conf-high" if confidence >= 75 else ("conf-medium" if confidence >= 45 else "conf-low")
            st.markdown(f"""
            <div class="confidence-wrap">
                <div class="confidence-label">AI Confidence</div>
                <div class="confidence-track">
                    <div class="confidence-fill {conf_class}" style="width:{confidence}%"></div>
                </div>
                <div class="confidence-pct">{confidence}%</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Risk flags ──
            risk_flags = result.get("risk_flags", [])
            if risk_flags:
                st.markdown('<div class="section-label">⚑ Risk Flags</div>', unsafe_allow_html=True)
                flags_html = " ".join(f'<span class="risk-flag">⚠ {f}</span>' for f in risk_flags)
                st.markdown(flags_html, unsafe_allow_html=True)

            # ── Reasoning ──
            st.markdown('<div class="section-label">Reasoning</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#333;line-height:1.65;margin:0'>{result.get('reasoning','')}</p>", unsafe_allow_html=True)

            # ── Tone ──
            st.markdown('<div class="section-label">Reporter Tone</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#666;font-style:italic;margin:0'>{result.get('tone','')}</p>", unsafe_allow_html=True)

            # ── Suggested response + copy button ──
            st.markdown('<div class="section-label">Suggested Response</div>', unsafe_allow_html=True)
            suggested = result.get("suggested_response", "")
            st.markdown(f'<div class="response-box">{suggested}</div>', unsafe_allow_html=True)
            st.code(suggested, language=None)

            # ── Tags ──
            tags = result.get("tags", [])
            if tags:
                st.markdown('<div class="section-label">Tags</div>', unsafe_allow_html=True)
                st.markdown(" ".join(f'<span class="tag">{t}</span>' for t in tags), unsafe_allow_html=True)

            # ── Process time ──
            st.markdown(f'<div class="process-time">⏱ Processed in {t_elapsed:.1f}s</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:0.72rem;color:#bbb;font-family:IBM Plex Mono,monospace'>"
    "Support Issue Reconstructor · Streamlit + OpenAI GPT-4o · Internal Support Tool"
    "</p>",
    unsafe_allow_html=True,
)
