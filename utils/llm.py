import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter

load_dotenv()

# load llm
def load_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in environment variables")

    return ChatOpenRouter(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        temperature=0.3,
    )