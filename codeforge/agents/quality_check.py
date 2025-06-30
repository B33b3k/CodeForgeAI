from ..prompts import QUALITY_CHECK_PROMPT
from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore

class QualityCheckAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(QUALITY_CHECK_PROMPT)
        )

    def run(self, code_review: str) -> bool:
        response = self.chain.invoke({"code_review": code_review})
        # Simple heuristic: look for 'True' in the response
        return "True" in response["text"]
