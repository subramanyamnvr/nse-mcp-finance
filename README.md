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
- `tools/stock_fundamentals.py`
- `tools/earnings_analyzer.py`
- `tools/portfolio_tracker.py`
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

## Implementation Plan (Incremental)
1. [x] Create server base
2. [x] Add A2A discovery endpoint
3. [x] Build stock fundamentals tool
4. [x] Register first tools with MCP endpoint
5. [x] Build earnings analyzer tool
6. [ ] Install MCP SDK (`pip install mcp`) and switch to official SDK server primitives
7. [ ] Build portfolio tracker tool
8. [ ] Add tool schemas
9. [ ] Test with MCP client
10. [ ] Containerize with Docker
11. [ ] Deploy with Cloud Build + Cloud Run
12. [ ] Write MCP + A2A integration guide

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

## Tech Stack
- Python MCP SDK
- FastAPI
- Cloud Run
- yfinance/NSE API
- GCP
