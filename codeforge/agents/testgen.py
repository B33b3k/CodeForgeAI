from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore

TESTGEN_PROMPT = """Write test code for the following {language} code. Output only the test code, no explanation.\n\nCode:\n{clean_code}"""

class TestGenAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(TESTGEN_PROMPT)
        )

    def run(self, language: str, clean_code: str) -> str:
        response = self.chain.invoke({"language": language, "clean_code": clean_code})
        return response["text"].strip()
