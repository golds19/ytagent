from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    messages = [
        (
            "system", 
            "You are a helpful assistant that translates English to French. Translate the user sentence"
        ),
        ("human", "I love programming in Python.")
    ]
    ai_msg = llm.invoke(messages)
    print(ai_msg.content)
