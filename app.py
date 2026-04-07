import streamlit as st
import json
import random
from logic.analyzer import analyze_issue
from logic.classifier import classify_and_enrich

st.set_page_config(
    page_title="Support Issue Reconstructor",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTextArea textarea { font-size: 0.9rem; }
    .metric-box {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .confidence-high { color: #1a7a4a; font-weight: 600; }
    .confidence-medium { color: #b45309; font-weight: 600; }
    .confidence-low { color: #b91c1c; font-weight: 600; }
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.4rem;
    }
    .event-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin-bottom: 0.3rem;
        line-height: 1.5;
    }
    .root-cause-block {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.25rem;
        border-radius: 0 6px 6px 0;
        margin-bottom: 1rem;
    }
    .fix-block {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem 1.25rem;
        border-radius: 0 6px 6px 0;
        margin-bottom: 1rem;
    }
    .repro-block {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.25rem;
        border-radius: 0 6px 6px 0;
        margin-bottom: 1rem;
    }
    hr { margin: 1.5rem 0; border-color: #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🔍 Support Issue Reconstructor")
st.caption("Reconstruct what happened — before the back-and-forth starts.")
st.markdown("---")

# ── Layout ──────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ── INPUT PANEL ─────────────────────────────────────────────────────────────
with left:
    st.subheader("Issue Input")

    issue_text = st.text_area(
        "Describe the issue",
        height=160,
        placeholder=(
            "e.g. A user says their automation stopped running after a teammate "
            "updated a shared configuration. The changes appear to have rolled back "
            "but the automation still isn't firing correctly."
        ),
    )

    category = st.selectbox(
        "Issue category",
        options=[
            "data inconsistency",
            "permissions / access",
            "automation / workflow",
            "sync / state",
            "unknown",
        ],
    )

    uploaded_file = st.file_uploader(
        "Upload event log (optional JSON)",
        type=["json"],
        help="Upload a JSON array of event objects. See /data/mock_events.json for format.",
    )

    use_mock = st.checkbox("Generate mock event log automatically", value=True)

    run = st.button("Reconstruct Issue", type="primary", use_container_width=True)

# ── OUTPUT PANEL ─────────────────────────────────────────────────────────────
with right:
    st.subheader("Reconstruction Output")

    if not run:
        st.info("Fill in the issue details on the left and click **Reconstruct Issue**.")
    else:
        if not issue_text.strip():
            st.warning("Please describe the issue before running.")
            st.stop()

        # Load or generate event log
        events = []
        if uploaded_file:
            try:
                events = json.load(uploaded_file)
            except Exception:
                st.error("Could not parse uploaded JSON. Falling back to mock events.")
                use_mock = True

        if not events and use_mock:
            from logic.classifier import generate_mock_events
            events = generate_mock_events(category)

        # Run analysis
        with st.spinner("Analyzing events and issue description…"):
            enriched = classify_and_enrich(issue_text, category, events)
            result = analyze_issue(enriched)

        # ── Event Timeline ────────────────────────────────────────────────
        with st.expander("📋 Reconstructed Event Timeline", expanded=True):
            if events:
                for evt in events:
                    ts = evt.get("timestamp", "")
                    actor = evt.get("actor", "system")
                    action = evt.get("action", "")
                    detail = evt.get("detail", "")
                    st.markdown(
                        f'<div class="event-entry">'
                        f'<span style="color:#89b4fa">{ts}</span>  '
                        f'<span style="color:#a6e3a1">[{actor}]</span>  '
                        f'<span style="color:#f9e2af">{action}</span>'
                        f'{"  — " + detail if detail else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No events available.")

        st.markdown("---")

        # ── Confidence Score ──────────────────────────────────────────────
        score = result.get("confidence_score", 0)
        if score >= 75:
            conf_class = "confidence-high"
            conf_label = "High"
        elif score >= 45:
            conf_class = "confidence-medium"
            conf_label = "Medium"
        else:
            conf_class = "confidence-low"
            conf_label = "Low"

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-label">Confidence Score</div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="{conf_class}" style="font-size:1.5rem">{score}/100</span> '
                f'<span style="color:#6b7280;font-size:0.85rem">({conf_label})</span>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown('<div class="section-label">Category</div>', unsafe_allow_html=True)
            st.markdown(f"**{category.title()}**")

        st.markdown("---")

        # ── Root Cause ────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Likely Root Cause</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="root-cause-block">{result["root_cause"]}</div>',
            unsafe_allow_html=True,
        )

        # ── Contributing Factors ──────────────────────────────────────────
        if result.get("contributing_factors"):
            st.markdown('<div class="section-label">Contributing Factors</div>', unsafe_allow_html=True)
            for factor in result["contributing_factors"]:
                st.markdown(f"- {factor}")

        st.markdown("---")

        # ── Suggested Fixes ───────────────────────────────────────────────
        st.markdown('<div class="section-label">Suggested Fixes</div>', unsafe_allow_html=True)
        fixes_html = "".join(f"<p style='margin:0 0 0.5rem'>✅ {fix}</p>" for fix in result["suggested_fixes"])
        st.markdown(f'<div class="fix-block">{fixes_html}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Reproduction Steps ────────────────────────────────────────────
        st.markdown('<div class="section-label">Reproduction Steps</div>', unsafe_allow_html=True)
        steps_html = "".join(
            f"<p style='margin:0 0 0.5rem'><strong>{i+1}.</strong> {step}</p>"
            for i, step in enumerate(result["reproduction_steps"])
        )
        st.markdown(f'<div class="repro-block">{steps_html}</div>', unsafe_allow_html=True)

        # ── Copy-ready summary ────────────────────────────────────────────
        st.markdown("---")
        with st.expander("📄 Copy-ready summary for ticket"):
            summary = f"""ROOT CAUSE
{result['root_cause']}

CONTRIBUTING FACTORS
{chr(10).join('- ' + f for f in result['contributing_factors'])}

SUGGESTED FIXES
{chr(10).join(str(i+1) + '. ' + fix for i, fix in enumerate(result['suggested_fixes']))}

REPRODUCTION STEPS
{chr(10).join(str(i+1) + '. ' + step for i, step in enumerate(result['reproduction_steps']))}

Confidence: {score}/100 ({conf_label})
"""
            st.code(summary, language=None)
