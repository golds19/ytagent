import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.pdf_utils import generate_pdf_bytes

# Load environment variables
load_dotenv()

# Constants
API_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def process_video(youtube_url: str):
    """Process video through backend API"""
    try:
        response = requests.post(
            f"{API_URL}/summarize",
            json={"youtube_url": youtube_url},
            timeout=1000
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out. The video might be too long or the server is busy.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to server: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="YouTube Video Summarizer",
        page_icon="📺",
        layout="wide"
    )

    # Initialize session state for results
    if "result" not in st.session_state:
        st.session_state.result = None

    if st.button("🏠 Home"):
        st.switch_page("app.py")

    st.title("📺 YouTube Video Summarizer")
    st.markdown("Get an AI-powered summary of any YouTube video. Just paste the URL below.")

    video_url = st.text_input(
        "Enter YouTube URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    if st.button("Generate Summary", type="primary", disabled=not video_url):
        with st.spinner("Processing video..."):
            result = process_video(video_url)
            if result:
                st.session_state.result = result  # Save to session state
                st.success("Video processed successfully!")

    # Display summary from session state if available
    if st.session_state.result:
        result = st.session_state.result

        st.subheader("📝 Summary")
        summaries_ = result.get("summaries", [])
        for summary in summaries_:
            st.markdown(summary.get("content", "No content available."))

        # Prepare PDF from summaries
        summary_texts = [s.get("content", "") if isinstance(s, dict) else str(s) for s in summaries_]
        pdf_bytes = generate_pdf_bytes(summary_texts)

        if pdf_bytes:
            st.download_button(
                label="Download Summary as PDF",
                data=pdf_bytes,
                file_name="summary.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
