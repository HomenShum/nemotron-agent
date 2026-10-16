# Nemotron 3 Ultra Agent

A developer exploring this repository is reviewing a small FastAPI chat service. Ordinary chat uses a one-node LangGraph graph; streaming calls the configured model client directly. Model access depends on an external OpenAI-compatible provider. The original overview and Agentbox deployment notes are retained below.

**Source review: 2026-10-15, [commit 641a52c](https://github.com/HomenShum/nemotron-agent/blob/641a52c5414700fc9a8c351045dbe716f5adbc09/app/main.py).** This preface supersedes setup or readiness implications in the retained notes. The app and setup findings below come from static source inspection; they are not installation, endpoint or model test results. Workflow run results must be checked for the specific revision being reviewed. Model availability, throughput and production readiness have not been established by this source inspection.

## Start with these files

| Entry point | What its source establishes |
| --- | --- |
| [app/main.py](app/main.py) | FastAPI application, provider configuration, request/response models and chat routes. |
| [requirements.txt](requirements.txt) | Eight pinned direct dependencies; installation and compatibility have not been tested here. |
| [Dockerfile](Dockerfile) | Declares Python 3.11, `uvicorn app.main:app`, port 8080 and two workers; its health command calls `/health`. This is a declaration, not a successful build or running container. |
| [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml) | Declares container packaging: PR builds omit registry push/signing; non-PR events build, publish to GHCR and sign. It does not exercise endpoints or provider/model access. Actual run results are revision-specific. |
| [CHANGELOG/README.md](CHANGELOG/README.md) | Index of documentation history and the small entry template. |

The application declares `GET /`, `GET /health`, `POST /chat` and `POST /chat/stream`; FastAPI's interactive documentation is exposed at `/docs`.

## Candidate local setup, derived from source

From the repository root in an isolated **Python 3.11** environment, the dependency and entrypoint declarations imply:

```sh
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

These commands were not run for this handoff. Before requesting chat, provide valid provider access through the process environment: `GMI_MAAS_API_KEY`, with `GMI_MAAS_BASE_URL` and `GMI_MODELS` set for the intended deployment. The code has defaults for the latter two and appends `/v1` to the configured base URL. It does not explicitly load a `.env` file. The original automatic-injection guidance below describes the intended Agentbox environment, not local setup; automatic injection was not verified.

## Concrete behavior and readiness limits

- **Local health is not model readiness.** `/health` returns status and configured model/base URL without calling the provider. A health response cannot prove authentication, model availability or a successful chat.
- **The caller supplies conversation history.** Each request carries `messages`; the graph is compiled without a checkpointer. `/chat` creates or echoes `session_id` but does not use it to load prior messages. A session identifier alone does not restore a conversation.
- **The two chat paths currently differ.** Source inspection shows `/chat` maps user, assistant and system roles. `/chat/stream` maps user and assistant roles, omitting system-role entries from `messages`; both paths support the separate `system_prompt` field. This is a static source observation, not a runtime/provider result, and no behavior change is included in this documentation handoff.
- **Streaming has a small text contract.** The source yields `data: <chunk content>\n\n`, then `data: [DONE]\n\n`. It does not define a JSON event schema or an explicit error event. Stream/client behavior has not been tested.

See [the README history](CHANGELOG/docs/readme.md) for the evidence and limits behind this handoff.

## Original overview and deployment notes (retained)

The following original text is preserved for project history. Interpret its deployment and model statements together with the source-review limits above.

A **LangGraph + FastAPI** agent powered by [Nemotron 3 Ultra](https://console.gmicloud.ai/user-console/ie/model-hub/llm/nemotron-3-ultra) on [GMI Cloud Agentbox](https://console.gmicloud.ai/user-console/ie/agentbox).

## Architecture

```
User Request
    │
    ▼
FastAPI (port 8080)
    │
    ▼
LangGraph StateGraph
    │
    ▼
ChatOpenAI → GMI MaaS (Nemotron 3 Ultra)
    │
    ▼
Response
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Agent info |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Single/multi-turn chat |
| `POST` | `/chat/stream` | Streaming chat (SSE) |
| `GET` | `/docs` | Swagger UI |

## Environment Variables

GMI Agentbox **auto-injects** these at runtime — do not set them manually:

| Variable | Description |
|----------|-------------|
| `GMI_MAAS_BASE_URL` | OpenAI-compatible base URL (`https://api.gmi-serving.com`) |
| `GMI_MAAS_API_KEY` | MaaS API key (injected by GMI) |
| `GMI_MODELS` | Model ID (`nvidia/nemotron-3-ultra-550b-a55b`) |

## Example Request

```bash
curl -X POST https://<your-agent-endpoint>/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain quantum entanglement in simple terms."}],
    "system_prompt": "You are a helpful AI assistant powered by Nemotron 3 Ultra."
  }'
```

## Deploy on GMI Agentbox

1. Push this repo to GitHub (Actions will build & push to GHCR automatically)
2. Make the GHCR package public
3. Register on GMI Agentbox with image: `ghcr.io/<your-username>/nemotron-agent:latest`
4. Select **Nemotron 3 Ultra** as the MaaS model
5. Set port mapping: `443 → 8080`
