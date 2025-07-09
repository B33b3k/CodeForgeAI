from .agents.preprocessor import PreprocessorAgent
from .agents.codegen import CodeGenAgent
from .agents.extractor import ExtractorAgent
from .agents.review import ReviewAgent
from .agents.quality_check import QualityCheckAgent
from .agents.testgen import TestGenAgent
from .agents.execute import ExecuteAgent
import os
import logging
import time

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")

# Setup logging
log_path = os.path.join(GENERATED_DIR, "logs.txt")
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path, mode='w')
    ]
)

class CodeForgeGraph:
    def __init__(self):
        self.preprocessor = PreprocessorAgent()
        self.codegen = CodeGenAgent()
        self.extractor = ExtractorAgent()
        self.review = ReviewAgent()
        self.quality = QualityCheckAgent()
        self.testgen = TestGenAgent()
        self.execute = ExecuteAgent()

    def run(self, initial_request: str):
        state = {
            "initial_request": initial_request,
            "task_spec": None,
            "language": None,
            "generated_code": None,
            "clean_code": None,
            "code_review": None,
            "review_passed": False,
            "test_code": None,
            "execution_output": None,
        }
        start_time = time.time()
        def elapsed():
            return time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))

        logging.info(f"PreprocessorAgent: Starting preprocessing")
        spec = self.preprocessor.run(initial_request)
        state.update(spec)
        logging.info(f"PreprocessorAgent: Extracted language={state.get('language')}, goal='{state.get('task_spec')}', inputs={state.get('inputs')}, outputs={state.get('outputs')}")
        if not state.get("language"):
            raise ValueError("Failed to extract language from the request. Please check your prompt or LLM output.")

        for loop in range(3):
            logging.info(f"CodeGenAgent: Starting code generation (attempt {loop+1})")
            state["generated_code"] = self.codegen.run(state["language"], state["task_spec"])
            code_lines = state["generated_code"].count('\n') + 1 if state["generated_code"] else 0
            logging.info(f"CodeGenAgent: Generated {code_lines} lines of {state['language']} code")

            logging.info(f"ExtractorAgent: Starting code extraction")
            state["clean_code"] = self.extractor.run(state["generated_code"])
            if not state["clean_code"] or len(state["clean_code"]) < 5:
                logging.info(f"ExtractorAgent: Code extraction failed, retrying...")
                continue
            logging.info(f"ExtractorAgent: Code extracted successfully")

            logging.info(f"ReviewAgent: Starting code review")
            state["code_review"] = self.review.run(state["language"], state["clean_code"])
            passed = self.quality.run(state["code_review"])
            state["review_passed"] = passed
            if passed:
                logging.info(f"ReviewAgent: Review passed. Summary: {state['code_review'][:100]}...")
                break
            else:
                logging.info(f"ReviewAgent: Review failed. Issues: {state['code_review'][:100]}...")
        else:
            logging.info(f"CodeGenAgent: Max attempts reached. Proceeding with last generated code.")

        if state["language"].lower() in ["python", "py"]:
            logging.info(f"TestGenAgent: Generating test code")
            state["test_code"] = self.testgen.run(state["language"], state["clean_code"])
            logging.info(f"TestGenAgent: Test code generated ({len(state['test_code'].splitlines())} lines)")
        if state["language"].lower() in ["python", "py"]:
            logging.info(f"ExecuteAgent: Starting code execution")
            state["execution_output"] = self.execute.run(state["language"], state["clean_code"])
            logging.info(f"ExecuteAgent: Execution output: {state['execution_output'][:100]}...")

        ext = self._get_ext(state["language"])
        with open(os.path.join(GENERATED_DIR, f"code.{ext}"), "w") as f:
            f.write(state["clean_code"] or "")
        if state["test_code"]:
            with open(os.path.join(GENERATED_DIR, f"test_code.{ext}"), "w") as f:
                f.write(state["test_code"])
        # No need to manually write logs here; FileHandler handles it
        with open(os.path.join(GENERATED_DIR, "logs.txt"), "a") as f:
            f.write(f"\nReview:\n{state['code_review']}\n\nExecution Output:\n{state['execution_output']}")
        return state

    def _get_ext(self, language):
        lang = language.lower()
        if lang in ["python", "py"]:
            return "py"
        if lang in ["javascript", "js"]:
            return "js"
        if lang in ["c++", "cpp"]:
            return "cpp"
        if lang in ["c"]:
            return "c"
        if lang in ["go", "golang"]:
            return "go"
        if lang in ["java"]:
            return "java"
        if lang in ["bash", "sh"]:
            return "sh"
        return "txt"
