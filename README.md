# AI Agents — Getting Started

This repository contains a small example agent that demonstrates how a
language model can request and invoke Python "tools" (functions) via a
conversational loop. The code is intentionally simple and educational so
beginners can follow along.

## Repository structure

- `main.py` — Example script showing the `ToolExecutor` class and a mock
  `get_temperature` tool.
- `.env` — (not committed) store sensitive keys here. **Do not commit** this
  file to the repository.

## Branching / level strategy

We keep multiple branches to show progressive levels of implementation:

- `llm_api_call` — Minimal working example: a mocked tool (no external APIs).
- `llm_suggesting_tools ` — LLM suggesting tool
- `ai_agent_at_work` — AI agent at work




## Step-by-step: Run the example locally

Prerequisites:

- Python 3.10+ (or compatible)
- A virtual environment (recommended)
- `GROWQ_API_KEY` set in your environment or in a local `.env` file

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (adjust if using `pipenv` / `poetry`)

```bash
python -m pip install -r requirements.txt || true
# If no requirements.txt exists, install packages manually
python -m pip install python-dotenv groq
```

3. Create a `.env` file in the project root and add your API key

```
GROWQ_API_KEY=sk-...replace-with-your-key...
```

4. Run the example

```bash
python main.py
```


## Notes and best practices

- Never commit `.env` or other secret files. Add `.env` to `.gitignore`.
- Use `--force-with-lease` when force-pushing rewritten history to be safer.
- Review protected branch & push-protection rules in your GitHub repository
  settings (secret scanning may block pushes that contain known secrets).

If you'd like, I can create the level branches for you and implement the
`level-2-api` example (replace mock temperature with a real weather API).
