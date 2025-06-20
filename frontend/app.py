import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from utils.pdf_utils import generate_pdf_bytes


def get_backend_url():
    """
    Determine backend URL based on environment
    Returns backend service URL if running in Docker, localhost if running locally
    """
    # Method 1: Check for explicit environment variable first
    backend_url = os.getenv("BACKEND_URL")
    if backend_url:
        return backend_url
    
    # Method 2: Check if explicitly told we're in Docker
    if os.getenv("RUNNING_IN_DOCKER", "").lower() == "true":
        return "http://backend:8000"
    
    # Method 3: Check for Docker indicators
    if os.path.exists("/.dockerenv"):
        return "http://backend:8000"
    
    # Method 4: Check hostname (Docker containers often have random hostnames)
    hostname = os.getenv("HOSTNAME", "")
    if len(hostname) == 12 or "docker" in hostname.lower():
        return "http://backend:8000"
    
    # Default to localhost (running locally)
    return "http://localhost:8000"


def make_backend_request(youtube_url, max_retries=2):
    """
    Make request to backend with fallback URLs
    """
    # Primary URL based on environment detection
    primary_url = get_backend_url()
    
    # Fallback URLs to try
    urls_to_try = [primary_url]
    
    # Add fallback if primary isn't localhost
    if primary_url != "http://localhost:8000":
        urls_to_try.append("http://localhost:8000")
    # Add fallback if primary isn't backend service
    if primary_url != "http://backend:8000":
        urls_to_try.append("http://backend:8000")
    
    last_error = None
    
    for i, url in enumerate(urls_to_try):
        try:
            st.info(f"🔗 Connecting to backend: {url}")
            
            response = requests.post(
                f"{url}/summarize",
                json={"youtube_url": youtube_url},
                timeout=30
            )
            
            if response.status_code == 200:
                st.success(f"✅ Connected successfully to: {url}")
                return response
            else:
                st.warning(f"⚠️ Got status {response.status_code} from {url}")
                last_error = f"Status {response.status_code}: {response.text}"
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Could not connect to {url}"
            st.warning(f"❌ {error_msg}")
            last_error = f"{error_msg}: {str(e)}"
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout connecting to {url}"
            st.warning(f"⏰ {error_msg}")
            last_error = f"{error_msg}: {str(e)}"
            
        except Exception as e:
            error_msg = f"Error with {url}"
            st.warning(f"❌ {error_msg}: {str(e)}")
            last_error = f"{error_msg}: {str(e)}"
    
    # If we get here, all URLs failed
    raise Exception(f"All backend connections failed. Last error: {last_error}")


st.set_page_config(page_title="Youtube Summarizer Agent", layout="wide")
st.title("Youtube Video Summarizer Powered by AI Agents")

# Show current backend URL for debugging
current_backend = get_backend_url()
st.sidebar.info(f"🔧 Backend URL: {current_backend}")

# Add environment info in sidebar for debugging
# st.sidebar.write("**Environment Info:**")
# st.sidebar.write(f"- Docker env: {os.path.exists('/.dockerenv')}")
# st.sidebar.write(f"- BACKEND_URL: {os.getenv('BACKEND_URL', 'Not set')}")
# st.sidebar.write(f"- RUNNING_IN_DOCKER: {os.getenv('RUNNING_IN_DOCKER', 'Not set')}")
# st.sidebar.write(f"- HOSTNAME: {os.getenv('HOSTNAME', 'Not set')}")

youtube_url = st.text_input("Enter Youtube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Summarize"):
    if not youtube_url:
        st.error("Please enter a YouTube URL")
    else:
        with st.spinner("Running AI agents..."):
            try:
                response = make_backend_request(youtube_url)
                data = response.json()

                # get summaries
                summary = data.get("summaries", [])
                st.subheader("📑Summary")
                st.markdown(summary if summary else "No summary available.")

                # get insights
                insights = data.get("insights", [])
                st.subheader("🔍Insights")
                st.markdown(insights if insights else "No insights available.")

                # generate and serve PDF
                pdf_bytes = generate_pdf_bytes(summary, insights)

                # show download button
                st.download_button(
                    label="Download Summary as PDF",
                    data=pdf_bytes,
                    file_name="youtube_summary.pdf",
                    mime="application/pdf",
                )

            except Exception as e:
                st.error(f"Failed to connect to API: {e}")
                st.error("Please check if the backend service is running.")


# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import streamlit as st
# import requests
# from utils.pdf_utils import generate_pdf_bytes


# st.set_page_config(page_title="Youtube Summarizer Agent", layout="wide")
# st.title("Youtube Video Summarizer Powered by AI Agents")

# youtube_url = st.text_input("Enter Youtube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# if st.button("Summarize"):
#     with st.spinner("Running AI agents..."):
#         try:
#             response = requests.post(
#                 "http://backend:8000/summarize",
#                 json={"youtube_url": youtube_url}
#             )
#             if response.status_code == 200:
#                 data = response.json()

#                 # get summaries
#                 summary = data.get("summaries", [])
#                 st.subheader("📑Summary")
#                 st.markdown(summary if summary else "No summary available.")

#                 # get insights
#                 insights = data.get("insights", [])
#                 st.subheader("🔍Insights")
#                 st.markdown(insights if insights else "No insights available.")

#                 # generate and serve PDF
#                 pdf_bytes = generate_pdf_bytes(summary, insights)

#                 # show download button
#                 st.download_button(
#                     label = "Download Summary as PDF",
#                     data = pdf_bytes,
#                     file_name = "youtube_summary.pdf",
#                     mime = "application/pdf",
#                 )

#             else:
#                 st.error(f"Error {response.status_code}: {response.text}")
#         except Exception as e:
#             st.error(f"Failed to connect to API: {e}")