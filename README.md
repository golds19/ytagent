# 🎥 YouTube Transcript Summarizer (AI Agents)

This project is an AI-powered web application that summarizes YouTube videos using only the transcript (no audio or Whisper model involved). It features a FastAPI backend for processing and a Streamlit frontend for user interaction. The system uses OpenAI models for summarization and insight generation.

## 🔧 Features

- Extracts transcript from YouTube videos
- Generates concise summaries and key insights
- Clean web interface with download-to-PDF support
- Built using FastAPI, Streamlit, and OpenAI APIs

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/golds19/ytagent.git
cd ytagent
````

### 2. Install dependencies

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Set up your environment

Create a `.env` file in the root directory and add your [OpenAI API key](https://platform.openai.com/account/api-keys):

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the backend server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Run the frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Access the app at [http://localhost:8501](http://localhost:8501)

## 🛠 Tech Stack

* **Frontend**: Streamlit
* **Backend**: FastAPI
* **LLM**: OpenAI (GPT-3.5/GPT-4)
* **PDF Generation**: FPDF
* **YouTube Transcript**: `youtube-transcript-api`

## 📌 Notes

* This version uses **only transcript data** (no audio or Whisper).
* Segmenter and open-source models like DeepSeek are not yet integrated.
* Docker support is planned for a future release.
