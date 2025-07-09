import argparse
from .graph import CodeForgeGraph
import os
import logging
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from threading import Thread
import time
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
import threading
from .utils import get_llm
from .utils import count_tokens


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
graph = CodeForgeGraph()

# In-memory task manager for demo (use Redis/DB for prod)
task_results: Dict[str, dict] = {}
task_logs: Dict[str, list] = {}
task_status: Dict[str, str] = {}
task_graphs: Dict[str, dict] = {}

agent_executor = None  # TODO: set this to your real agent_executor

# Gemini free tier: 16,000 tokens/request, 2,000,000 tokens/month (as of 2024)
token_limit = 2_000_000
used_tokens = 0
per_task_tokens = {}

def log_for_task(task_id, message):
    timestamp = time.strftime('%H:%M:%S', time.localtime())
    entry = f"[{timestamp}] {message}"
    task_logs.setdefault(task_id, []).append(entry)
    logging.info(f"[Task {task_id}] {message}")

@app.get("/agents")
async def get_agents():
    return {
        "agents": [
            "PreprocessorAgent",
            "CodeGenAgent",
            "ExtractorAgent",
            "ReviewAgent",
            "QualityAgent",
            "TestGenAgent",
            "ExecuteAgent"
        ]
    }

@app.post("/generate")
async def generate_code(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    task = data.get("task")
    agent_order = data.get("agent_order") 
    if not task:
        return JSONResponse(status_code=400, content={"error": "Missing 'task' in request body"})
    task_id = str(uuid.uuid4())
    task_status[task_id] = "pending"
    log_for_task(task_id, "Task received. Queued for processing.")
    background_tasks.add_task(run_pipeline_task, task_id, task, agent_order)
    return {"task_id": task_id, "status": "pending"}

def run_pipeline_task(task_id, task, agent_order=None):
    global used_tokens
    try:
        default_order = [
            "PreprocessorAgent",
            "CodeGenAgent",
            "ExtractorAgent",
            "ReviewAgent",
            "QualityAgent",
            "TestGenAgent",
            "ExecuteAgent"
        ]
        order = agent_order if agent_order else default_order
        state = {"initial_request": task}
        task_status[task_id] = "running"
        # --- Dynamic graph tracking ---
        nodes = []
        edges = []
        node_positions = {}
        last_agent = None
        y_base = 0
        for i, agent in enumerate(order):
            node_id = agent
            nodes.append({
                "id": node_id,
                "data": {"label": agent},
                "position": {"x": i * 250, "y": y_base}
            })
            node_positions[agent] = (i * 250, y_base)
            if last_agent:
                edges.append({
                    "id": f"edge-{last_agent}-{agent}",
                    "source": last_agent,
                    "target": agent,
                    "type": "smoothstep",
                    "animated": True
                })
            last_agent = agent
        # Special: after ExtractorAgent, both ReviewAgent and TestGenAgent run in parallel
        if "ExtractorAgent" in order and "ReviewAgent" in order and "TestGenAgent" in order:
            idx = order.index("ExtractorAgent")
            if idx + 1 < len(order) and order[idx+1] in ["ReviewAgent", "TestGenAgent"]:
                # Remove the edge from ExtractorAgent to the next agent
                edges = [e for e in edges if not (e["source"] == "ExtractorAgent")]
                # Add parallel edges
                if "ReviewAgent" in order:
                    edges.append({
                        "id": "edge-ExtractorAgent-ReviewAgent",
                        "source": "ExtractorAgent",
                        "target": "ReviewAgent",
                        "type": "smoothstep",
                        "animated": True
                    })
                if "TestGenAgent" in order:
                    edges.append({
                        "id": "edge-ExtractorAgent-TestGenAgent",
                        "source": "ExtractorAgent",
                        "target": "TestGenAgent",
                        "type": "smoothstep",
                        "animated": True
                    })
                # Both ReviewAgent and TestGenAgent connect to ExecuteAgent if present
                if "ExecuteAgent" in order:
                    if "ReviewAgent" in order:
                        edges.append({
                            "id": "edge-ReviewAgent-ExecuteAgent",
                            "source": "ReviewAgent",
                            "target": "ExecuteAgent",
                            "type": "smoothstep",
                            "animated": True
                        })
                    if "TestGenAgent" in order:
                        edges.append({
                            "id": "edge-TestGenAgent-ExecuteAgent",
                            "source": "TestGenAgent",
                            "target": "ExecuteAgent",
                            "type": "smoothstep",
                            "animated": True
                        })
        task_graphs[task_id] = {"nodes": nodes, "edges": edges}
        per_task_tokens[task_id] = 0
        for agent in order:
            if agent == "PreprocessorAgent":
                log_for_task(task_id, "PreprocessorAgent: Starting preprocessing")
                spec = graph.preprocessor.run(task)
                # Count tokens for preprocessor
                pre_tokens = count_tokens(task)
                used_tokens += pre_tokens
                per_task_tokens[task_id] += pre_tokens
                log_for_task(task_id, f"PreprocessorAgent: Extracted language={spec.get('language')}, goal='{spec.get('task_spec')}', inputs={spec.get('inputs')}, outputs={spec.get('outputs')}")
                if not spec.get("language"):
                    raise ValueError("Failed to extract language from the request. Please check your prompt or LLM output.")
                state.update(spec)
            elif agent == "CodeGenAgent":
                for loop in range(3):
                    log_for_task(task_id, f"CodeGenAgent: Starting code generation (attempt {loop+1})")
                    state["generated_code"] = graph.codegen.run(state["language"], state["task_spec"])
                    # Count tokens for codegen
                    codegen_tokens = count_tokens(state["task_spec"])
                    used_tokens += codegen_tokens
                    per_task_tokens[task_id] += codegen_tokens
                    code_lines = state["generated_code"].count('\n') + 1 if state["generated_code"] else 0
                    log_for_task(task_id, f"CodeGenAgent: Generated {code_lines} lines of {state['language']} code")
                    log_for_task(task_id, f"ExtractorAgent: Starting code extraction")
                    state["clean_code"] = graph.extractor.run(state["generated_code"])
                    # Count tokens for extractor
                    extractor_tokens = count_tokens(state["generated_code"])
                    used_tokens += extractor_tokens
                    per_task_tokens[task_id] += extractor_tokens
                    if not state["clean_code"] or len(state["clean_code"]) < 5:
                        log_for_task(task_id, f"ExtractorAgent: Code extraction failed, retrying...")
                        continue
                    log_for_task(task_id, f"ExtractorAgent: Code extracted successfully")
                    # --- Parallel execution of ReviewAgent and TestGenAgent ---
                    review_result = {}
                    testgen_result = {}
                    threads = []
                    def run_review():
                        global used_tokens, per_task_tokens
                        log_for_task(task_id, f"ReviewAgent: Starting code review")
                        review = graph.review.run(state["language"], state["clean_code"])
                        review_tokens = count_tokens(state["clean_code"])
                        used_tokens += review_tokens
                        per_task_tokens[task_id] += review_tokens
                        review_result["review"] = review
                        passed = graph.quality.run(review)
                        quality_tokens = count_tokens(review)
                        used_tokens += quality_tokens
                        per_task_tokens[task_id] += quality_tokens
                        review_result["review_passed"] = passed
                        log_for_task(task_id, f"ReviewAgent: Review {'passed' if passed else 'failed'}. Summary: {review[:100]}...")
                    def run_testgen():
                        global used_tokens, per_task_tokens
                        if state["language"].lower() in ["python", "py", "javascript", "js"]:
                            log_for_task(task_id, f"TestGenAgent: Generating test code")
                            test_code = graph.testgen.run(state["language"], state["clean_code"])
                            testgen_tokens = count_tokens(state["clean_code"])
                            used_tokens += testgen_tokens
                            per_task_tokens[task_id] += testgen_tokens
                            testgen_result["test_code"] = test_code
                            log_for_task(task_id, f"TestGenAgent: Test code generated ({len(test_code.splitlines())} lines)")
                    t1 = threading.Thread(target=run_review)
                    t2 = threading.Thread(target=run_testgen)
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()
                    state["code_review"] = review_result.get("review")
                    state["review_passed"] = review_result.get("review_passed")
                    state["test_code"] = testgen_result.get("test_code")
                    if state["review_passed"]:
                        break
                    else:
                        log_for_task(task_id, f"ReviewAgent: Review failed. Issues: {state['code_review'][:100]}...")
                else:
                    log_for_task(task_id, f"CodeGenAgent: Max attempts reached. Proceeding with last generated code.")
            elif agent == "ExecuteAgent":
                if state.get("language", "").lower() in ["python", "py"]:
                    log_for_task(task_id, f"ExecuteAgent: Starting code execution")
                    state["execution_output"] = graph.execute.run(state["language"], state["clean_code"])
                    exec_tokens = count_tokens(state["clean_code"])
                    used_tokens += exec_tokens
                    per_task_tokens[task_id] += exec_tokens
                    log_for_task(task_id, f"ExecuteAgent: Execution output: {state['execution_output'][:100]}...")
        ext = graph._get_ext(state["language"])
        code_path = f"generated/code.{ext}"
        clean_code = state.get("clean_code") if state else None
        if isinstance(clean_code, str) and clean_code:
            with open(code_path, "w") as f:
                f.write(clean_code)
        test_code = state.get("test_code") if state else None
        if isinstance(test_code, str) and test_code:
            with open(f"generated/test_code.{ext}", "w") as f:
                f.write(test_code)
        log_for_task(task_id, f"Files saved: {code_path}, generated/test_code.{ext if state.get('test_code') else ''}")
        task_results[task_id] = {
            "language": state["language"],
            "task_spec": state["task_spec"],
            "code": state["clean_code"],
            "test_code": state.get("test_code"),
            "review": state.get("code_review"),
            "execution_output": state.get("execution_output"),
            "code_file": code_path,
            "test_file": f"generated/test_code.{ext}" if state.get("test_code") else None,
            "logs_file": "generated/logs.txt",
            "tokens_used": per_task_tokens[task_id],
            "tokens_remaining": max(0, token_limit - used_tokens),
            "token_limit": token_limit
        }
        task_status[task_id] = "complete"
        log_for_task(task_id, "Task complete.")
    except Exception as e:
        task_status[task_id] = "error"
        log_for_task(task_id, f"Error: {str(e)}")
        task_results[task_id] = {"error": str(e)}

@app.get("/tokens")
async def get_tokens():
    return {
        "used": used_tokens,
        "remaining": max(0, token_limit - used_tokens),
        "limit": token_limit
    }

@app.get("/logs/{task_id}")
async def get_logs(task_id: str):
    logs = task_logs.get(task_id, [])
    def log_stream():
        for entry in logs:
            yield entry + "\n"
    return StreamingResponse(log_stream(), media_type="text/plain")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = task_status.get(task_id, "not_found")
    return {
        "task_id": task_id,
        "status": status,
        "tokens_used": per_task_tokens.get(task_id, 0),
        "tokens_remaining": max(0, token_limit - used_tokens),
        "token_limit": token_limit
    }

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = task_results.get(task_id)
    if not result:
        return JSONResponse(status_code=404, content={"error": "Task not found or not complete yet."})
    return result

@app.get("/graph/{task_id}")
async def get_agent_graph_data(task_id: str):
    """
    Returns the dynamic agent graph for the given task_id in React Flow format.
    """
    try:
        graph = task_graphs.get(task_id)
        if not graph:
            # Return a minimal placeholder graph instead of 404
            return {
                "nodes": [
                    {"id": "start", "data": {"label": "No graph found for this task yet."}, "position": {"x": 0, "y": 0}}
                ],
                "edges": []
            }
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    parser = argparse.ArgumentParser(description="CodeForgeAI: Automated code generation, testing, and review.")
    parser.add_argument('--task', type=str, help='Natural language code generation request')
    parser.add_argument('--api', action='store_true', help='Run as FastAPI server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='API host')
    parser.add_argument('--port', type=int, default=8000, help='API port')
    args = parser.parse_args()

    if args.api:
        uvicorn.run("codeforge.main:app", host=args.host, port=args.port, reload=False)
        return

    if not args.task:
        print("You must provide --task for CLI mode.")
        return
    # CLI mode: log to console only
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    state = graph.run(args.task)
    ext = graph._get_ext(state["language"])
    print("\n=== CodeForgeAI Output ===")
    print(f"Language: {state['language']}")
    print(f"Task: {state['task_spec']}")
    print(f"Code saved to: generated/code.{ext}")
    if state.get('test_code'):
        print(f"Test code saved to: generated/test_code.{ext}")
    print(f"Review: {state['code_review']}")
    if state.get('execution_output'):
        print(f"Execution output: {state['execution_output']}")
    print(f"Logs saved to: generated/logs.txt")

if __name__ == "__main__":
    main()
