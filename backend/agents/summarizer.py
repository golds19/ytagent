# from langchain.chat_models import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

# loading the environment variables from the .env file
load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini-2024-07-18")

def summarize_segment(text):
    prompt = f"Please summarize the following transcript segment, highlighting the key points and main ideas:\n\n{text}\n\nSummary:"
    result =  llm.invoke(prompt)

    return result.content

def summarizer_node(state):
    transcript = state["transcript"]
    summaries = summarize_segment(transcript)
    #summaries = [summarize_segment(segment) for segment in segments]
    return {"summaries": summaries}