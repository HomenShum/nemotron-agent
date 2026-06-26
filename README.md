# Nemotron 3 Ultra Agent

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
