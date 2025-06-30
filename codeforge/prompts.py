# prompts.py

PREPROCESSOR_PROMPT = """
**Task: Analyze and Decompose a Software Development Request**

**Objective:**
Based on the user's request provided below, generate a structured specification document. The specification should be clear, concise, and suitable for a developer to begin work.

**User Request:**
"{initial_request}"

**Output Specification:**
Respond with a JSON object containing the following keys:
- "language": (string) The primary programming language required.
- "functionality_goal": (string) A detailed, one-sentence description of the core functionality.
- "inputs": (array of strings) A list of expected inputs, including their types or formats.
- "outputs": (array of strings) A list of expected outputs, detailing what the code should produce.
- "constraints": (array of strings) A list of any limitations, requirements, or specific rules to be followed.
"""

CODEGEN_PROMPT = """
**Task: Code Generation**

**Language:** {language}
**Specification:** {task_spec}

**Instructions:**
Generate a complete, production-quality code solution based on the provided specification. The output should contain *only* the raw code for the specified language, enclosed in a single markdown code block.

**Coding Standards:**
1.  **Robustness:** Implement comprehensive error and exception handling.
2.  **Input Validation:** Validate all inputs to prevent errors and ensure security.
3.  **Logging:** Integrate logging for key events and debugging purposes. For Python, use the `logging` module.
4.  **Clarity:** Adhere to language-specific style guides (e.g., PEP 8 for Python) and include concise comments where necessary.
5.  **Status Reporting:** Return clear status messages or structured error objects instead of ambiguous values like None.
"""

EXTRACTOR_PROMPT = """
**Task: Isolate Code Block**

**Input:**
```
{generated_code}
```

**Instruction:**
From the input provided above, extract and return *only* the content within the first code block. Omit all surrounding text, explanations, and markdown formatting.
"""

REVIEW_PROMPT = """
**Task: Perform a Code Review**

**Language:** {language}

**Code for Review:**
```
{clean_code}
```

**Review Criteria:**
Please assess the code based on the following criteria:
- **Correctness:** Does the code meet its functional requirements?
- **Readability & Style:** Is the code clean, well-formatted, and easy to understand?
- **Maintainability:** Is the code modular and extensible?
- **Security:** Are there any potential vulnerabilities (e.g., injection, insecure handling of data)?

**Output:**
Provide a concise, summary review. If the code is of high quality, a simple confirmation like "Code is well-structured and meets all criteria." is sufficient. If issues are found, list them as bullet points.
"""

QUALITY_CHECK_PROMPT = """
**Task: Analyze Code Review Sentiment**

**Review Text:**
"{code_review}"

**Instruction:**
Analyze the sentiment of the provided code review. Determine if it constitutes an approval or a rejection.

**Output:**
Respond with a single boolean value in JSON format: `{{"review_passed": boolean}}`.
- `true`: The review is positive, indicating approval (e.g., mentions "looks good," "no issues," "well-written," "acceptable").
- `false`: The review is negative or raises concerns that require action.
"""

EXECUTION_PROMPT = """
**Task: Sandbox Code Execution**

**Language:** {language}

**Code to Execute:**
```
{clean_code}
```

**Instruction:**
Execute the provided code within a secure, isolated sandbox environment. Capture and return all standard output (stdout) and standard error (stderr) streams generated during execution.
"""