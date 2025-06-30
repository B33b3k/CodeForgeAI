# CodeForgeAI

## Overview

**CodeForgeAI** is a full-stack, multi-agent, AI-powered code generation platform. It enables users to submit natural language coding tasks and receive high-quality, tested, and reviewed code, with a live visual representation of the agent pipeline. The system is designed for extensibility, transparency, and collaboration, leveraging modern AI, multi-agent orchestration, and a beautiful, interactive frontend.

---

## Architecture

### 1. **Frontend (React + TypeScript + Tailwind CSS)**
- **Modern UI:** Built with React, TypeScript, Tailwind CSS, Framer Motion, and Lucide icons.
- **Task Submission:** Users describe the code they want; the UI supports prompt templates and agent chain customization.
- **Live Log Viewer:** See real-time logs as agents process the task.
- **Result Panel:** View generated code, tests, reviews, and execution output with syntax highlighting and copy/download options.
- **Agent Graph Visualizer:** Interactive React Flow graph shows the agent pipeline and execution path for each task.
- **Dark Mode:** Toggle for light/dark themes.

### 2. **Backend (FastAPI + Python)**
- **API Endpoints:**
  - `/generate`: Start a new code generation task.
  - `/status/{task_id}`: Poll for task status.
  - `/result/{task_id}`: Fetch the result (code, tests, review, execution output).
  - `/logs/{task_id}`: Stream or fetch logs for a task.
  - `/agents`: List available agents and their order.
  - `/graph/{task_id}`: Return the agent execution graph for visualization.
- **Task Management:** In-memory (can be extended to Redis/DB for production).
- **CORS Enabled:** Allows frontend-backend communication across origins.

### 3. **Multi-Agent System (CodeForgeGraph)**
- **Agents:**
  - **PreprocessorAgent:** Parses and structures the user's request.
  - **CodeGenAgent:** Generates code based on the task spec.
  - **ExtractorAgent:** Cleans and extracts the generated code.
  - **ReviewAgent:** Reviews the code for quality and correctness.
  - **QualityAgent:** Assesses review results for pass/fail.
  - **TestGenAgent:** Generates tests for the code (if applicable).
  - **ExecuteAgent:** Runs the code and captures output (for supported languages).
- **Pipeline:** Agents are chained, with some (Review/TestGen) running in parallel for efficiency.
- **Dynamic Graph:** The backend tracks the actual agent execution path for each task, enabling live visualization.

---

## Features

- **Natural Language to Code:** Users describe what they want; the system delivers code, tests, and review.
- **Multi-Agent Orchestration:** Modular agents handle preprocessing, codegen, extraction, review, testing, and execution.
- **Live Logs:** Real-time feedback on agent progress and issues.
- **Agent Chain Customization:** Users can reorder agents for custom workflows.
- **Agent Graph Visualization:** See the pipeline and execution path for each task.
- **Downloadable Artifacts:** (Planned) Download code, tests, and logs as a ZIP.
- **Task History:** (Planned) Browse and revisit previous tasks and results.
- **Authentication:** (Planned) User accounts and private task history.
- **Extensible:** Add new agents, models, or integrations easily.

---

## Problems Solved

- **Transparency:** Users see exactly how their code is generated, tested, and reviewed, with live logs and a visual agent graph.
- **Quality Assurance:** Automated review and test generation ensure higher code quality.
- **Extensibility:** Modular agent design allows for easy addition of new capabilities (e.g., linters, deployers, custom tools).
- **User Empowerment:** Users can customize the agent pipeline and prompt, tailoring the system to their needs.
- **Collaboration:** (Planned) Commenting, rating, and sharing features foster a collaborative coding environment.

---

## Workflow

1. **User submits a task** via the frontend (e.g., "Write a Python function to compute Fibonacci numbers").
2. **Backend creates a task** and starts the agent pipeline.
3. **Agents process the task** in sequence (with some parallelism), logging progress and results.
4. **Frontend polls for status, logs, and results.**
5. **When complete,** the frontend displays the code, tests, review, execution output, and the agent execution graph.
6. **User can download artifacts** (planned), comment, or start a new task.

---

## How to Run

1. **Backend:**
   ```sh
   cd codeforge
   pip install -r requirements.txt
   python -m codeforge.main --api
   ```
2. **Frontend:**
   ```sh
   cd codeforge-frontend
   npm install
   npm start
   ```
3. **Open** [http://localhost:3000](http://localhost:3000) in your browser.

---

## Future Directions

- **Task history and persistence** (database integration)
- **User authentication and profiles**
- **Multi-file/project generation**
- **Downloadable project artifacts**
- **Live agent status in graph**
- **Collaboration and feedback tools**
- **Model selection and advanced prompt engineering**
- **Integrations with GitHub, CI/CD, and more**

---

## Authors & Credits
- Built with ❤️ by the CodeForgeAI team.
- Powered by FastAPI, React, LangChain, and open-source AI tools.

## Setup
1. Clone this repo and `cd codeforge`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file (see `.env` for example):
   - For OpenAI:
     ```env
     USE_PROVIDER=openai
     OPENAI_API_KEY=your_openai_key
     ```
   - For Gemini:
     ```env
     USE_PROVIDER=gemini
     GOOGLE_API_KEY=your_gemini_api_key
     ```

## Usage
Run from the `codeforge` directory:
```bash
python main.py --task "Write a Go function to reverse a linked list"
```

Outputs will be saved in `generated/`:
- `code.<ext>`: The generated code
- `test_code.<ext>`: Generated test code (if supported)
- `logs.txt`: Review and execution logs

## Supported Languages
- Code generation: Any
- Test generation: Python, JS, Go, etc.
- Execution: Python (MVP), JS (planned)

## Architecture
- Modular agents (preprocessing, codegen, review, etc.)
- LangGraph pipeline with review and extraction loops
- Easily extensible for more languages and features

---
MIT License 