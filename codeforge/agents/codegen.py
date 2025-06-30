from ..prompts import CODEGEN_PROMPT
from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore

class CodeGenAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(CODEGEN_PROMPT)
        )

    def run(self, language: str, task_spec: str) -> str:
        response = self.chain.invoke({"language": language, "task_spec": task_spec})
        return response["text"]
