import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from utils.pdf_utils import generate_pdf_bytes


st.set_page_config(page_title="Youtube Summarizer Agent", layout="wide")
st.title("Youtube Video Summarizer Powered by AI Agents")

youtube_url = st.text_input("Enter Youtube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Summarize"):
    with st.spinner("Running AI agents..."):
        try:
            response = requests.post(
                "http://localhost:8000/summarize",
                json={"youtube_url": youtube_url}
            )
            if response.status_code == 200:
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
                    label = "Download Summary as PDF",
                    data = pdf_bytes,
                    file_name = "youtube_summary.pdf",
                    mime = "application/pdf",
                )

            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")