# youtube-summarizer/app/services/summarizer.py

import openai
from textwrap import wrap

openai.api_key = "your-openai-api-key"  # Replace with env var in production

# Split transcript into manageable chunks (~1500 tokens)
def split_text(text, max_words=800):
    sentences = text.split('. ')
    chunks, current = [], []
    total_words = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if total_words + word_count > max_words:
            chunks.append('. '.join(current) + '.')
            current, total_words = [], 0
        current.append(sentence)
        total_words += word_count
    if current:
        chunks.append('. '.join(current) + '.')
    return chunks

def summarize_chunk(text_chunk, model="gpt-4"):
    prompt = (
        "You are a helpful assistant. Summarize the following transcript chunk:\n\n"
        f"{text_chunk}\n\n"
        "Focus on the main topics and arguments. Return the summary as bullet points."
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional transcript summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response['choices'][0]['message']['content']

def summarize_transcript(full_transcript):
    chunks = split_text(full_transcript)
    summaries = [summarize_chunk(chunk) for chunk in chunks]

    final_summary_prompt = (
        "Combine the following bullet point summaries into a concise high-level summary:\n\n"
        + "\n\n".join(summaries)
    )

    final_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional summarizer."},
            {"role": "user", "content": final_summary_prompt}
        ],
        temperature=0.3
    )
    return final_response['choices'][0]['message']['content']

# Usage:
# from app.services.summarizer import summarize_transcript
# summary = summarize_transcript(full_transcript)
