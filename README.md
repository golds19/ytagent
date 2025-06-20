# 🎬 YouTube Transcript Summarizer

A lightweight app that summarizes YouTube videos using their transcripts with the help of OpenAI's language models. Built with **FastAPI** (backend) and **Streamlit** (frontend), this project provides a clean and responsive interface for quick insights from YouTube content.

---

## 🚀 Features

- 📄 Summarizes video transcripts (no audio processing).
- ⚡ Powered by OpenAI's LLM (GPT-based).
- 🖥️ Dual interface: FastAPI backend + Streamlit frontend.
- 📦 Clean modular codebase, ready for extension.

---

## 🔧 Tech Stack

- **Backend:** FastAPI, LangChain, OpenAI
- **Frontend:** Streamlit
- **Other Libraries:** fpdf, youtube-transcript-api, pydantic, dotenv
- **Deployment Ready:** Docker support (CI/CD + local setup)

---

## 🧠 Requirements

- Python 3.10+
- An OpenAI API Key

---

## 📦 Installation & Running Locally

### 1. Clone the Repo

```bash
git clone https://github.com/golds/ytagent.git
cd ytagent
````

### 2. Set Up the Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Add Your API Key

Create a `.env` file in the root directory and add:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run Backend (FastAPI)

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Run Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

---

## 🐳 Run with Docker Compose

To run the app using **prebuilt Docker Hub images**:

### 1. Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    image: benphil/yt-summarizer-backend:latest
    container_name: yt-backend
    ports:
      - "8000:8000"
    env_file:
      - .env

  frontend:
    image: benphil/yt-summarizer-frontend:latest
    container_name: yt-frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

### 2. Add Your `.env` File

```env
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the App

```bash
docker-compose up
```

To stop:

```bash
docker-compose down
```

---

## 🔄 CI/CD (GitHub Actions + Docker Hub)

This project supports CI/CD using GitHub Actions to automatically build and push Docker images to Docker Hub upon pushing to `main`.
---

## 📌 Notes

* This version **does not use Whisper/audio**, only transcript-based.
* **No open-source models** are integrated yet.
* Segmenter Agent is **not used** in this version.
* Docker and Whisper integration are planned for future updates.

---

## ✨ Future Improvements

* Add Whisper for transcript generation from raw audio.
* Integrate open-source LLMs like DeepSeek or Mistral.
* Advanced CI/CD (multi-stage builds, tests).
* Frontend enhancements with richer visual summaries.
