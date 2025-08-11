import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Page config
    st.set_page_config(
        page_title="AI-Powered Content Summarizer",
        page_icon="📝",
        layout="wide"
    )

    # CSS Styles
    st.markdown("""
        <style>
        /* General page style */
        body {
            background-color: #f8f9fa;
            font-family: "Segoe UI", sans-serif;
        }
        /* Centered title and subtitle */
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            text-align: center;
            color: #555;
            margin-bottom: 2rem;
        }
        /* Card style */
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }
        .card h3 {
            color: #1f77b4;
            margin-bottom: 10px;
        }
        .card p {
            color: #555;
            font-size: 0.95rem;
        }
        .card ul {
            text-align: left;
            margin: 15px 0 0;
            padding-left: 20px;
            font-size: 0.9rem;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title and subtitle
    st.markdown("<div class='main-title'>📝 AI-Powered Content Summarizer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Welcome! Choose the type of content you want to summarize.</div>", unsafe_allow_html=True)

    # Cards container
    col1, col2 = st.columns(2, gap="large")

    # YouTube Card
    with col1:
        if st.button("📺 YouTube Video", key="yt_card", help="Go to YouTube Summarizer"):
            st.switch_page("pages/youtube_summarizer.py")
        st.markdown("""
            <div class="card">
                <h3>📺 YouTube Video</h3>
                <p>Summarize YouTube videos with AI-powered analysis</p>
                <ul>
                    <li>Transcription</li>
                    <li>Key points extraction</li>
                    <li>Chapter generation</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Webpage Card
    with col2:
        if st.button("🌐 Webpage", key="web_card", help="Go to Webpage Summarizer"):
            st.switch_page("pages/webpage_summarizer.py")
        st.markdown("""
            <div class="card">
                <h3>🌐 Webpage</h3>
                <p>Extract and summarize content from any webpage</p>
                <ul>
                    <li>Content extraction</li>
                    <li>Smart filtering</li>
                    <li>Concise summaries</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # About section
    with st.expander("ℹ️ About Content Summarizer"):
        st.markdown("""
        This tool combines multiple AI technologies to provide intelligent content summarization:
        
        **YouTube Summarizer**
        - Transcribes videos automatically
        - Analyzes content for key points
        - Generates structured chapter summaries
        - Handles videos in multiple languages
        
        **Webpage Summarizer**
        - Extracts relevant content from any webpage
        - Filters out ads and irrelevant content
        - Creates concise, readable summaries
        - Preserves important context and details
        
        Perfect for:
        - Research and study
        - Content analysis
        - Quick information extraction
        - Knowledge management
        """)

if __name__ == "__main__":
    main()
