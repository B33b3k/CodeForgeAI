from ..prompts import EXTRACTOR_PROMPT
from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore
import re

class ExtractorAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(EXTRACTOR_PROMPT)
        )

    def run(self, generated_code: str) -> str:
        response = self.chain.invoke({"generated_code": generated_code})
        text = response["text"].strip()
        # Remove code block markers like ```python, ```go, etc.
        code = re.sub(r'^```[a-zA-Z0-9_+-]*\s*', '', text)
        code = re.sub(r'```$', '', code)
        return code.strip()
