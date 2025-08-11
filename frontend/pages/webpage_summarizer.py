import streamlit as st
import requests
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Constants
API_URL =  os.getenv('BACKEND_URL', 'http://localhost:8000')

def get_webpage_summary(url: str) -> tuple[Optional[str], Optional[dict]]:
    """Call the backend API to get webpage summary"""
    try:
        response = requests.post(
            f"{API_URL}/api/webpage/summarize",
            json={"url": url},
            timeout=300
        )
        response.raise_for_status()
        
        # Extract data from response
        data = response.json()
        if data:
            return data.get("summary"), data.get("metadata")
        else:
            error_msg = data.get("error", "Unknown error occurred")
            st.error(f"Server error: {error_msg}")
            return None, None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server took too long to respond.")
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to server: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

def main():
    # Page config
    st.set_page_config(
        page_title="Webpage Summarizer",
        page_icon="🌐",
        layout="wide"
    )
    
    # Add home button
    if st.button("🏠 Home"):
        st.switch_page("app.py")
    
    # Title and description
    st.title("🌐 Webpage Summarizer")
    st.markdown("""
    Get a concise summary of any webpage. Simply enter the URL below.
    """)
    
    # URL input
    url = st.text_input(
        "Enter webpage URL",
        placeholder="https://example.com/article"
    )
            
    # Main functionality
    if st.button("Generate Summary", type="primary", disabled=not url):
        with st.spinner("Analyzing webpage..."):
            summary, metadata = get_webpage_summary(url)
            
            if summary:
                st.success("Summary generated successfully!")
                
                # Display summary in a nice container
                with st.container():
                    st.markdown("### 📝 Summary")
                    st.markdown(summary)
                    
                    # Add copy button
                    if st.button("📋 Copy Summary"):
                        st.write(
                            f'<script>navigator.clipboard.writeText("{summary}");</script>',
                            unsafe_allow_html=True
                        )
                        st.success("Summary copied to clipboard!")
                    
                    # Display metadata if available
                    if metadata:
                        with st.expander("📊 Article Metadata"):
                            st.markdown(f"""
                            - **Word Count**: {metadata.get('word_count', 'N/A')}
                            - **Length**: {metadata.get('length', 'N/A')} characters
                            - **Processed**: {metadata.get('timestamp', 'N/A')}
                            """)

if __name__ == "__main__":
    main() 