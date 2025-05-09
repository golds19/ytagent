from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

# loading the environment variables from the .env file
load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini-2024-07-18")

def extract_insights(summary):
    """
    Extracts insights from a list of summaries using the LLM.
    """
    combined_summaries = summary
    prompt = f"""From the following summary, extract key insights, action items, and notable points. Return the result as bullet points:\n\n{combined_summaries}"""
    key_insights = llm.invoke(prompt)
    return key_insights.content

def insight_node(state):
    return {"insights": extract_insights(state["summaries"])}