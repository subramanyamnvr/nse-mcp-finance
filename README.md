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
