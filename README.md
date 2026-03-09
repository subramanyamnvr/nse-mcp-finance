# mcp-finance-server

## Overview
Incremental MCP finance tools server with A2A (agent-to-agent) discoverability.

## Skills Demonstrated
- MCP (Model Context Protocol)
- A2A (Agent-to-Agent) discovery
- Tool building for AI agents
- Cloud Run deployment
- Financial data integration
- API design

## Project Structure
- `server.py`
- `mcp_stdio_server.py`
- `MCP_A2A_INTEGRATION_GUIDE.md`
- `tools/stock_fundamentals.py`
- `tools/earnings_analyzer.py`
- `tools/portfolio_tracker.py`
- `scripts/mcp_smoke_test.py`
- `Dockerfile`
- `cloudbuild.yaml`

## Current Progress
- Module 1 completed: server bootstrap + A2A discovery card
  - `GET /health` for uptime checks
  - `GET /.well-known/agent.json` as an A2A agent card
- Module 2 completed: first MCP-exposed finance tool
  - `POST /mcp` with JSON-RPC methods: `tools/list`, `tools/call`
  - `stock_fundamentals` implemented in `tools/stock_fundamentals.py`
  - `health_check` and `stock_fundamentals` registered in MCP tool registry
- Module 3 completed: earnings analyzer module
  - `earnings_analyzer` implemented in `tools/earnings_analyzer.py`
  - `earnings_analyzer` registered in both MCP registry and A2A agent card
- Module 4 completed: portfolio tracker module
  - `portfolio_tracker` implemented in `tools/portfolio_tracker.py`
  - Calculates per-position current value and P/L, plus portfolio totals
  - Registered in MCP registry and A2A agent card
- Module 5 completed: run + containerize setup
  - Added `requirements.txt`
  - Added runnable `Dockerfile`
  - Added `cloudbuild.yaml` deployment pipeline for Cloud Run
- Module 6 completed: MCP client smoke-test module
  - Added `scripts/mcp_smoke_test.py`
  - Validates `tools/list` and `tools/call` (`health_check`) over HTTP JSON-RPC
- Module 7 completed: official MCP SDK server module
  - Added `mcp_stdio_server.py` using `mcp.server.fastmcp.FastMCP`
  - Registered the same tools (`health_check`, `stock_fundamentals`, `earnings_analyzer`, `portfolio_tracker`)
  - Keeps FastAPI HTTP mode and MCP stdio mode side-by-side for demos
- Module 8 completed: A2A task execution API
  - Added `POST /a2a/tasks` to create agent tasks (`call_tool`)
  - Added `GET /a2a/tasks/{task_id}` to poll task status/result
  - Reused existing tool execution path for MCP + A2A parity
- Module 9 completed: API contract validation
  - Added Pydantic request models for `/mcp` and `/a2a/tasks`
  - Invalid `tools/call` params now return JSON-RPC `-32602` (`Invalid params`)
  - Improves predictable request/response behavior for MCP clients
- Module 10 completed: MCP + A2A integration guide
  - Added `MCP_A2A_INTEGRATION_GUIDE.md`
  - Documents architecture, flows, examples, and production next steps

## Implementation Plan (Incremental)
1. [x] Create server base
2. [x] Add A2A discovery endpoint
3. [x] Build stock fundamentals tool
4. [x] Register first tools with MCP endpoint
5. [x] Build earnings analyzer tool
6. [x] Build portfolio tracker tool
7. [x] Add runtime dependencies and basic container/deploy setup
8. [x] Add tool schemas
9. [x] Test with MCP client (smoke test script)
10. [x] Containerize with Docker
11. [x] Deploy with Cloud Build + Cloud Run (pipeline file added)
12. [x] Add official MCP SDK server entrypoint
13. [x] Add A2A task execution endpoint
14. [x] Add API request validation models
15. [x] Write MCP + A2A integration guide

## Business Value
Extends any AI assistant with live Indian market data.

## MCP + A2A Design
- MCP handles structured tool execution between client and server.
- A2A card (`/.well-known/agent.json`) helps other agents discover:
  - server identity
  - supported protocols
  - available/planned tools
  - endpoint locations
- Together:
  - MCP = how tools are invoked
  - A2A = how agents find and understand each other
  - A2A task API = how agents can request/track work asynchronously

Detailed walkthrough: [`MCP_A2A_INTEGRATION_GUIDE.md`](./MCP_A2A_INTEGRATION_GUIDE.md)

## MCP Request Examples
List tools:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Call stock fundamentals:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "stock_fundamentals",
    "arguments": {
      "symbol": "INFY",
      "exchange": "NSE"
    }
  }
}
```

Call earnings analyzer:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "earnings_analyzer",
    "arguments": {
      "symbol": "TCS",
      "exchange": "NSE"
    }
  }
}
```

Call portfolio tracker:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "portfolio_tracker",
    "arguments": {
      "default_exchange": "NSE",
      "holdings": [
        {"symbol": "INFY", "quantity": 10, "average_buy_price": 1450},
        {"symbol": "TCS", "quantity": 4, "average_buy_price": 3600}
      ]
    }
  }
}
```

## How To Run
Local run:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Run official MCP SDK server (stdio):
```powershell
python mcp_stdio_server.py
```
Use this mode with MCP-native clients that launch servers as subprocesses.

Health check:
```powershell
curl http://127.0.0.1:8000/health
```

MCP tools list:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/mcp" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

If you want cURL syntax in PowerShell, use `curl.exe` (not `curl` alias):
```powershell
curl.exe -X POST "http://127.0.0.1:8000/mcp" ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}"
```

Run MCP smoke test client:
```powershell
python scripts/mcp_smoke_test.py --base-url http://127.0.0.1:8000
```

A2A task create:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/a2a/tasks" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"action":"call_tool","tool_name":"stock_fundamentals","arguments":{"symbol":"INFY","exchange":"NSE"},"requester":"demo-agent"}'
```

A2A task poll:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/a2a/tasks/<task_id>" -Method Get
```

Invalid params example (`-32602`):
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/mcp" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":99,"method":"tools/call","params":{"arguments":{}}}'
```

Docker run:
```powershell
docker build -t nse-mcp-finance:local .
docker run --rm -p 8080:8080 nse-mcp-finance:local
```

## Tech Stack
- Python MCP SDK
- FastAPI
- Cloud Run
- yfinance/NSE API
- GCP
