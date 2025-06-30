from ..prompts import REVIEW_PROMPT
from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore

class ReviewAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(REVIEW_PROMPT)
        )

    def run(self, language: str, clean_code: str) -> str:
        response = self.chain.invoke({"language": language, "clean_code": clean_code})
        return response["text"].strip()
