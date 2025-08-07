import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Page config
    st.set_page_config(
        page_title="Content Summarizer",
        page_icon="📝",
        layout="wide"
    )
    
    # Add custom CSS for clickable cards
    st.markdown("""
        <style>
        .card {
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            height: 100%;
            background-color: white;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-color: #1f77b4;
        }
        .card h3 {
            margin-bottom: 15px;
            color: #1f77b4;
        }
        .card ul {
            text-align: left;
            margin-top: 15px;
            padding-left: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the title and description
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>📝 Content Summarizer</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Welcome to Content Summarizer! Choose the type of content you want to summarize.</p>", unsafe_allow_html=True)
    
    # Create a centered container for the main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <h3 style='text-align: center;'>Choose Your Summarization Tool</h3>
        <p style='text-align: center;'>Select the type of content you want to analyze and summarize:</p>
        """, unsafe_allow_html=True)
        
        # Create two cards for the different features
        col_yt, col_web = st.columns(2)
        
        # YouTube Card
        with col_yt:
            youtube_clicked = st.markdown("""
            <div class="card" onclick="window.location.href='YouTube_Summarizer'">
                <h3>📺 YouTube Video</h3>
                <p>Summarize YouTube videos with AI-powered analysis</p>
                <ul>
                    <li>Transcription</li>
                    <li>Key points extraction</li>
                    <li>Chapter generation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button for navigation (activated by JavaScript)
            if st.button("YouTube", key="yt_nav", help="Navigate to YouTube Summarizer"):
                st.switch_page("pages/youtube_summarizer.py")
        
        # Webpage Card
        with col_web:
            webpage_clicked = st.markdown("""
            <div class="card" onclick="window.location.href='Webpage_Summarizer'">
                <h3>🌐 Webpage</h3>
                <p>Extract and summarize content from any webpage</p>
                <ul>
                    <li>Content extraction</li>
                    <li>Smart filtering</li>
                    <li>Concise summaries</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button for navigation (activated by JavaScript)
            if st.button("Webpage", key="web_nav", help="Navigate to Webpage Summarizer"):
                st.switch_page("pages/webpage_summarizer.py")
    
    # Add JavaScript for handling card clicks
    st.markdown("""
        <script>
        // Add click event listeners to cards
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('click', function() {
                // Find and click the corresponding hidden button
                const tool = this.querySelector('h3').textContent.includes('YouTube') ? 'yt_nav' : 'web_nav';
                document.querySelector(`button[kind="primary"][data-testid="${tool}"]`).click();
            });
        });
        </script>
    """, unsafe_allow_html=True)
    
    # Add about section in an expander at the bottom
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
            
            Both tools use advanced Natural Language Processing to ensure high-quality, 
            relevant summaries that capture the essence of the content while removing noise 
            and redundancy.
            
            Perfect for:
            - Research and study
            - Content analysis
            - Quick information extraction
            - Knowledge management
            """)

if __name__ == "__main__":
    main()