# Agentic Website Builder (Study Project)

This repository is a **personal learning project** focused on studying **agentic development** with multiple specialized AI agents.

It is not a production-ready product, not a framework, and not intended for commercial use in its current state.

## What This Project Is

A sequential multi-agent pipeline that takes a website idea and generates:

- refined product requirements
- market/competitor research
- content strategy
- design system
- generated images
- multi-file front-end project
- QA validation feedback
- Docker deployment instructions

## Important Disclaimer

This project exists for:

- experimentation
- architecture learning
- prompt/agent workflow studies
- tool-calling exploration with OpenAI APIs

It may generate imperfect outputs, inconsistent quality, or invalid project artifacts depending on prompts and model responses.

## High-Level Workflow

Current orchestrated flow in `src/core/orchestration/orchestrator.py`:

1. `ProductManagerAgent`
   - refines requirements interactively (up to 3 iterations)
   - expects `REQUIREMENTS_READY` to finalize structured requirements
2. `ResearcherAgent`
   - performs real web searches via `WebSearchService`
   - returns strategic research JSON
3. `ContentDesignerAgent`
   - builds conversion-oriented content structure
4. `DesignerAgent`
   - produces structured `design_system` JSON
5. `ImageGenerator` (service stage in orchestrator)
   - generates image files from design prompts into `workspace/assets/images/`
6. `DeveloperAgent`
   - generates multi-file website JSON (`files` map)
7. `QAAgent`
   - validates project structure and quality (up to 3 QA revision iterations)
8. `DevOpsAgent`
   - provides deployment instructions and Docker guidance

## Project Structure

```text
src/
  agents/
    product_manager/
    researcher/
    content_designer/
    designer/
    developer/
    qa/
    devops/
  core/
    base_agent.py
    llm.py
    web_search.py
    image_generator.py
    orchestration/orchestrator.py
main.py
docker/
workspace/
```

## Tech Stack

- Python 3.11+
- OpenAI Python SDK (`openai`)
- Multi-agent orchestration via custom classes
- Docker + nginx output support

## Setup

1. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variable:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Run

```bash
python3 main.py
```

The script will prompt:

```text
Enter your website requirement:
```

Then it executes the full agent workflow and prints stage logs plus final output.

## Generated Outputs

- Website files: `workspace/` (HTML/CSS/JS/assets)
- Generated images: `workspace/assets/images/`
- Dockerfile for static serving: `docker/Dockerfile`

## Current Limitations

- Heavy dependency on model output correctness
- Limited schema enforcement/retries for malformed responses
- No persistent memory/state beyond current run
- No formal test suite for full orchestration behavior

## Why This Exists

This codebase is intentionally built as a **hands-on study project** to understand:

- agent role decomposition
- orchestration loops and guardrails
- tool integration (web search, image generation)
- structured intermediate artifacts across agents

If you use it, treat it as a sandbox for learning and experimentation.
