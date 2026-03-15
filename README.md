# Agentic Website Builder (Study Project)

This repository is a **personal learning project** focused on studying **agentic development** with multiple specialized AI agents.

It is not a production-ready product, not a framework, and not intended for commercial use in its current state.

## What This Project Is

A sequential multi-agent pipeline that takes a website idea and generates:

- refined product requirements
- market/competitor research
- editorial website content structure
- technical architecture specification
- design system
- implementation task plan
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
   - returns strategic insights plus factual knowledge-base JSON
3. `ContentDesignerAgent`
   - generates site structure and editorial website content from research
4. `ArchitectAgent`
   - produces a structured technical architecture specification
5. `DesignerAgent`
   - produces structured `design_system` JSON plus image generation specs
6. `PlannerAgent`
   - breaks the implementation into executable development tasks
7. `ImageGenerator` (service stage in orchestrator)
   - generates image files from design prompts into `workspace/assets/images/`
8. `DeveloperAgent`
   - generates multi-file website JSON by rendering `site_structure`
9. `QAAgent`
   - validates structure, accessibility, responsiveness, architecture alignment, and rendered site content, including deterministic site_structure-to-HTML checks (up to 3 QA revision iterations)
10. `DevOpsAgent`
   - provides deployment instructions and Docker guidance

Primary orchestrator artifacts:

- `product_requirements`
- `research_output`
- `site_structure`
- `architecture_spec`
- `design_spec`
- `development_tasks`
- `generated_files`

The orchestrator now passes these artifacts between stages as structured JSON payloads and logs artifact summaries at every stage for easier debugging.

## Project Structure

```text
src/
  agents/
    architect/
    product_manager/
    researcher/
    content_designer/
    designer/
    planner/
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

The development tooling in `requirements.txt` also includes `pytest`, `black`, `flake8`, and `pre-commit`.

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

## Testing And Local Quality Checks

Run the full test suite:

```bash
make test
```

Run the full suite with coverage using the helper script:

```bash
bash scripts/run_tests.sh
```

Run lint checks locally:

```bash
make lint
```

Format the codebase locally:

```bash
make format
```

You can also run the tools directly without `make`:

```bash
python3 -m pytest -q
python3 -m flake8 src tests main.py
python3 -m black src tests main.py
```

To run tests with coverage manually after activating the virtual environment:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

## Pre-commit Hooks

Install the Git pre-commit hooks locally:

```bash
python3 -m pre_commit install
```

Run all configured hooks manually:

```bash
python3 -m pre_commit run --all-files
```

The pre-commit configuration in `.pre-commit-config.yaml` runs:

- `black`
- `flake8`
- `pytest`

## Current Limitations

- Heavy dependency on model output correctness
- Lightweight schema validation currently covers research, content, architecture, design, and planning outputs
- No persistent memory/state beyond current run
- Full end-to-end orchestration still depends on live OpenAI API access outside mocked tests

## Why This Exists

This codebase is intentionally built as a **hands-on study project** to understand:

- agent role decomposition
- spec-driven planning workflows
- orchestration loops and guardrails
- tool integration (web search, image generation)
- structured intermediate artifacts across agents

If you use it, treat it as a sandbox for learning and experimentation.
