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

# --- Token counting utility ---
def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 chars for English)
        return max(1, len(text) // 4)

def get_llm():
    provider = os.getenv("USE_PROVIDER", "openai")
    if provider == "gemini" and ChatGoogleGenerativeAI:
        
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    if ChatOpenAI:
        return ChatOpenAI(model="gpt-3.5-turbo")
    raise ImportError("No supported LLM provider found. Please install langchain_openai or langchain_google_genai.")
