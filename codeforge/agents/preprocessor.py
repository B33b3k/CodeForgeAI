from ..prompts import PREPROCESSOR_PROMPT
from ..utils import get_llm
from langchain_core.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore
import re

class PreprocessorAgent:
    def __init__(self):
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=PromptTemplate.from_template(PREPROCESSOR_PROMPT)
        )

    def run(self, initial_request: str) -> dict:
        response = self.chain.invoke({"initial_request": initial_request})
        print("Raw LLM response (preprocessor):", response)  # Debugging line
        text = response.get("text") if isinstance(response, dict) else str(response)
        lines = text.splitlines() if text else []
        result = {"initial_request": initial_request}
        # Regex patterns for robust extraction
        patterns = {
            "language": re.compile(r"- \*\*?Language:?\*\*?\s*:?\s*(.+)", re.IGNORECASE),
            "task_spec": re.compile(r"- \*\*?Functionality Goal:?\*\*?\s*:?\s*(.+)", re.IGNORECASE),
            "inputs": re.compile(r"- \*\*?Inputs:?\*\*?\s*:?\s*(.+)", re.IGNORECASE),
            "outputs": re.compile(r"- \*\*?Outputs:?\*\*?\s*:?\s*(.+)", re.IGNORECASE),
            "constraints": re.compile(r"- \*\*?Constraints:?\*\*?\s*:?\s*(.+)", re.IGNORECASE),
        }
        for line in lines:
            for key, pat in patterns.items():
                m = pat.match(line.strip())
                if m:
                    result[key] = m.group(1).strip(" *:")
        # Fallback: try to extract language with regex if not found
        if not result.get("language") and text:
            match = re.search(r"(?i)language\s*[:\-]?\s*([A-Za-z0-9\+\#]+)", text)
            if match:
                result["language"] = match.group(1)
        return result
