# ai-support-agent

A customer-support AI agent built with **LangGraph**. It answers order-status questions by calling a tool against a REST API instead of making answers up.

> **Status: work in progress.** What works today is listed below; the roadmap shows what comes next.

## What it does today

- **Agent loop with LangGraph:** model → tool → model, until the model has an answer
- **Tool calling:** `get_order_status` queries a mock Orders REST API (FastAPI)
- **Free LLM by default:** Google Gemini (AI Studio free tier); OpenAI is optional via `LLM_PROVIDER=openai`
- **CLI chat:** ask one question or chat interactively
- **14 tests** that need no network and no API key (fake LLM, mocked HTTP)

## Design choices

- **LLM-generated arguments are untrusted:** order IDs must be digits only, so a value like `../admin` never reaches the URL
- **Tool errors are returned as text, not raised:** the agent can explain a failure to the customer
- **Minimal data:** the tool returns only what is needed to answer (no customer name)
- **Step limit:** `MAX_GRAPH_STEPS` stops runaway tool loops (covered by a test)
- **Prompt hardening:** the system prompt tells the model that tool output is data, not instructions
- **Testable by design:** tool logic is separate from the decorator, and the agent takes the LLM as a parameter

## Architecture

```
question → agent node (LLM) ⇄ tools node (get_order_status → Orders API)
                  ↓
               answer
```

## Quick start

Tested on Python 3.14.

```powershell
git clone https://github.com/moha10-hub/ai-support-agent.git
cd ai-support-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Get a free API key at https://aistudio.google.com/apikey and put it in `.env` after `GOOGLE_API_KEY=`.

Terminal 1, the mock Orders API:

```powershell
python -m uvicorn orders_api.main:app --port 8001
```

Terminal 2, the agent (it answers in Italian):

```powershell
python -m app.cli "Dov'è il mio ordine 1001?"
```

Demo orders: `1001` shipped, `1002` in preparation, `1003` delivered.

## Tests

```powershell
python -m pytest -q
```

## Configuration (`.env`)

| Variable | Meaning | Default |
|---|---|---|
| `LLM_PROVIDER` | `gemini` or `openai` | `gemini` |
| `GOOGLE_API_KEY` | Free key from Google AI Studio | – |
| `LLM_MODEL` | Model name (empty = provider default) | `gemini-3.5-flash-lite` |
| `ORDERS_API_URL` | Orders API address | `http://127.0.0.1:8001` |

Note: on the Gemini free tier, Google may use prompts to improve its products, so use only fake data.

## Roadmap

- [ ] RAG tool for FAQs and policies (using my [RAG backend](https://github.com/moha10-hub/rag-fastapi-backend))
- [ ] Conversation memory
- [ ] Retry and error handling for provider rate limits
- [ ] Human-in-the-loop approval before creating support tickets
- [ ] Docker Compose setup