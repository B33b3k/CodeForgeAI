import os
from dotenv import load_dotenv
load_dotenv()
try:
    from langchain_openai import ChatOpenAI  # type: ignore
except ImportError:
    ChatOpenAI = None
try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
except ImportError:
    ChatGoogleGenerativeAI = None

def get_llm():
    provider = os.getenv("USE_PROVIDER", "openai")
    if provider == "gemini" and ChatGoogleGenerativeAI:
        
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    if ChatOpenAI:
        return ChatOpenAI(model="gpt-3.5-turbo")
    raise ImportError("No supported LLM provider found. Please install langchain_openai or langchain_google_genai.")
