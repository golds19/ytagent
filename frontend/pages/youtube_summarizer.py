import os
import sys
import requests
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.pdf_utils import generate_repurpose_pdf

load_dotenv()

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ReelifyAI — Repurpose",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu, header, footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.block-container {
    padding-top: 2rem !important;
    max-width: 780px;
}

/* Page background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0F0F1A;
}

/* Back button */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(108,99,255,0.3) !important;
    color: #a89dff !important;
    border-radius: 50px !important;
    padding: 6px 18px !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #6C63FF !important;
}

/* Primary generate button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF, #9b8fff) !important;
    border: none !important;
    color: #fff !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 14px 32px !important;
    border-radius: 50px !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(108,99,255,0.5) !important;
}

/* Page heading */
.page-title {
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 0%, #c4bfff 60%, #6C63FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.page-subtitle {
    color: #7070a0;
    font-size: 0.95rem;
    margin-bottom: 28px;
}

/* Output card */
.output-card {
    background: #1A1A2E;
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 12px;
    line-height: 1.7;
    color: #E0E0F0;
    font-size: 0.97rem;
}

/* Tweet card */
.tweet-card {
    background: #1A1A2E;
    border: 1px solid rgba(108,99,255,0.15);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
    position: relative;
}
.tweet-num {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6C63FF;
    margin-bottom: 8px;
}
.tweet-text {
    color: #E0E0F0;
    font-size: 0.97rem;
    line-height: 1.6;
    margin-bottom: 8px;
}
.tweet-count {
    font-size: 0.75rem;
    color: #50507a;
    text-align: right;
}
.tweet-count.warn { color: #f0a500; }
.tweet-count.over { color: #e05555; }

/* Error card */
.error-card {
    background: rgba(224, 85, 85, 0.1);
    border: 1px solid rgba(224, 85, 85, 0.35);
    border-radius: 12px;
    padding: 18px 22px;
    color: #e08080;
    font-size: 0.92rem;
}

/* Tab styling */
[data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
}
[data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* Section label */
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6C63FF;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


def repurpose_video(url: str):
    try:
        resp = requests.post(
            f"{API_URL}/repurpose",
            json={"url": url},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.Timeout:
        return None, "Request timed out. The video might be too long or the server is busy."
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"Server error: {detail}"
    except requests.exceptions.RequestException as e:
        return None, f"Could not connect to the server: {str(e)}"


def char_count_class(n: int) -> str:
    if n > 280:
        return "over"
    if n > 250:
        return "warn"
    return ""


# ── UI ────────────────────────────────────────────────────────────────────────

if st.button("← Back", type="secondary"):
    st.switch_page("app.py")

st.markdown("<div class='page-title'>Repurpose a YouTube Video</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>Paste any YouTube link and get your content package instantly.</div>", unsafe_allow_html=True)

url_input = st.text_input(
    label="YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

generate_clicked = st.button(
    "Generate Content ✨",
    type="primary",
    disabled=not url_input.strip(),
)

if "repurpose_result" not in st.session_state:
    st.session_state.repurpose_result = None
if "repurpose_error" not in st.session_state:
    st.session_state.repurpose_error = None

if generate_clicked and url_input.strip():
    st.session_state.repurpose_result = None
    st.session_state.repurpose_error = None
    with st.spinner("Fetching transcript & crafting your content package..."):
        result, error = repurpose_video(url_input.strip())
    if error:
        st.session_state.repurpose_error = error
    else:
        st.session_state.repurpose_result = result

# ── Error ─────────────────────────────────────────────────────────────────────
if st.session_state.repurpose_error:
    st.markdown(
        f"<div class='error-card'>⚠️ {st.session_state.repurpose_error}</div>",
        unsafe_allow_html=True,
    )

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.repurpose_result:
    data = st.session_state.repurpose_result
    summary = data.get("summary", "")
    tweets = data.get("tweet_thread", [])
    blog = data.get("blog_intro", "")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📄  Summary", "🐦  Tweet Thread", "✍️  Blog Intro"])

    # ── Summary tab ───────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<div class='section-label'>Video Summary</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-card'>{summary}</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label' style='margin-top:16px'>Copy</div>", unsafe_allow_html=True)
        st.code(summary, language="")

    # ── Tweet thread tab ──────────────────────────────────────────────────────
    with tab2:
        st.markdown("<div class='section-label'>5-Tweet Thread</div>", unsafe_allow_html=True)
        all_tweets_text = "\n\n".join(
            f"[{i+1}/5] {t}" for i, t in enumerate(tweets)
        )
        for i, tweet in enumerate(tweets):
            n = len(tweet)
            cls = char_count_class(n)
            st.markdown(f"""
<div class="tweet-card">
    <div class="tweet-num">Tweet {i + 1} of {len(tweets)}</div>
    <div class="tweet-text">{tweet}</div>
    <div class="tweet-count {cls}">{n}/280</div>
</div>""", unsafe_allow_html=True)
        st.markdown("<div class='section-label' style='margin-top:16px'>Copy All Tweets</div>", unsafe_allow_html=True)
        st.code(all_tweets_text, language="")

    # ── Blog intro tab ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("<div class='section-label'>Blog Introduction</div>", unsafe_allow_html=True)
        # Render paragraphs separated by blank lines
        paragraphs = [p.strip() for p in blog.split("\n") if p.strip()]
        blog_html = "".join(f"<p style='margin-bottom:1em'>{p}</p>" for p in paragraphs)
        st.markdown(f"<div class='output-card'>{blog_html}</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label' style='margin-top:16px'>Copy</div>", unsafe_allow_html=True)
        st.code(blog, language="")

    # ── PDF download ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        pdf_bytes = generate_repurpose_pdf(data)
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_bytes,
            file_name="reelifyai-content-package.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")
