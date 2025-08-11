import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_URL = 'http://localhost:8000'

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
    # Page config
    st.set_page_config(
        page_title="YouTube Video Summarizer",
        page_icon="📺",
        layout="wide"
    )
    
    # Add home button
    if st.button("🏠 Home"):
        st.switch_page("app.py")
    
    # Title and description
    st.title("📺 YouTube Video Summarizer")
    st.markdown("""
    Get an AI-powered summary of any YouTube video. Just paste the URL below.
    """)
    
    # URL input
    video_url = st.text_input(
        "Enter YouTube URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    
    # Process button
    if st.button("Generate Summary", type="primary", disabled=not video_url):
        with st.spinner("Processing video..."):
            result = process_video(video_url)
            
            if result:
                st.success("Video processed successfully!")
                
                # Display summary sections
                with st.container():
                    st.subheader("📝 Summary")
                    if result.get("summaries"):
                        for summary in result["summaries"]:
                            # Assuming each summary is a dictionary with a 'content' key
                            st.markdown(summary.get("content", "No content available."))  # Display the content of the summary
                    else:
                        st.markdown("No summaries available.")
                    
                    # Display chapters if available
                    # if "chapters" in result:
                    #     st.subheader("📚 Chapters")
                    #     for chapter in result["chapters"]:
                    #         st.markdown(f"**{chapter['title']}**")
                    #         st.markdown(chapter['content'])
                    
                    # Display metadata
                    # with st.expander("📊 Video Metadata"):
                    #     st.markdown(f"""
                    #     - **Title**: {result.get("metadata", {}).get("title", "N/A")}
                    #     - **Duration**: {result.get("metadata", {}).get("duration", "N/A")}
                    #     - **Channel**: {result.get("metadata", {}).get("channel", "N/A")}
                    #     """)

if __name__ == "__main__":
    main() 