import streamlit as st

st.set_page_config(
    page_title="ReelifyAI — Content Repurposing Engine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding-top: 0 !important; }
[data-testid="stSidebar"] { display: none; }

/* Page background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0F0F1A;
}

/* Hero section */
.hero {
    text-align: center;
    padding: 80px 20px 60px;
    max-width: 800px;
    margin: 0 auto;
}
.hero-badge {
    display: inline-block;
    background: rgba(108, 99, 255, 0.15);
    border: 1px solid rgba(108, 99, 255, 0.4);
    color: #a89dff;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 20px;
    margin-bottom: 28px;
}
.hero-title {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    line-height: 1.18;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #fff 0%, #c4bfff 50%, #6C63FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #9090b0;
    margin-bottom: 40px;
    line-height: 1.6;
}

/* CTA button override — target the Streamlit primary button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF, #9b8fff) !important;
    border: none !important;
    color: #fff !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 14px 40px !important;
    border-radius: 50px !important;
    letter-spacing: 0.03em !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.35) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(108,99,255,0.5) !important;
}

/* Feature cards */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 900px;
    margin: 60px auto 20px;
    padding: 0 20px;
}
.feature-card {
    background: #1A1A2E;
    border: 1px solid rgba(108, 99, 255, 0.15);
    border-radius: 16px;
    padding: 28px 24px;
    transition: transform 0.2s, border-color 0.2s;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(108, 99, 255, 0.45);
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 14px;
}
.feature-title {
    font-size: 1rem;
    font-weight: 700;
    color: #E8E8F0;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.88rem;
    color: #7070a0;
    line-height: 1.55;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 40px auto;
    max-width: 900px;
}

/* Footer */
.footer {
    text-align: center;
    color: #40405a;
    font-size: 0.8rem;
    padding: 30px 0 40px;
}
.footer span {
    color: #6C63FF;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✨ Content Repurposing Engine</div>
    <div class="hero-title">Turn any YouTube video<br>into a full content package</div>
    <div class="hero-subtitle">
        Paste a link — get a polished summary, a ready-to-post tweet thread,<br>
        and a compelling blog intro. In seconds.
    </div>
</div>
""", unsafe_allow_html=True)

col_l, col_btn, col_r = st.columns([3, 2, 3])
with col_btn:
    if st.button("Start Repurposing →", type="primary", use_container_width=True):
        st.switch_page("pages/youtube_summarizer.py")

# ── Feature cards ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="features-grid">
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">Smart Summary</div>
        <div class="feature-desc">
            A crisp 3-sentence paragraph capturing the core message,
            main insight, and key takeaway — ready to share anywhere.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🐦</div>
        <div class="feature-title">Tweet Thread</div>
        <div class="feature-desc">
            A 5-tweet thread with a hook, key points, and a
            call-to-action — formatted and under 280 chars each.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">✍️</div>
        <div class="feature-title">Blog Intro</div>
        <div class="feature-desc">
            Three compelling paragraphs that hook readers, set context,
            and preview your article — ready to drop into any CMS.
        </div>
    </div>
</div>
<hr class="divider"/>
<div class="footer">
    Built with ♥ by <span>ReelifyAI</span> &mdash; No account required.
</div>
""", unsafe_allow_html=True)
