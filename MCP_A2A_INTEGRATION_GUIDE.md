# MCP + A2A Integration Guide

## Purpose
This project supports two complementary interaction styles:
- MCP for structured tool discovery and invocation.
- A2A for agent discovery and task-style agent-to-agent requests.

Use this guide when explaining architecture in demos, interviews, or articles.

## Architecture
- HTTP app: `server.py`
  - `GET /health`
  - `GET /.well-known/agent.json`
  - `POST /mcp`
  - `POST /a2a/tasks`
  - `GET /a2a/tasks/{task_id}`
- MCP SDK app: `mcp_stdio_server.py`
  - Stdio MCP server (`FastMCP`) for MCP-native clients.

## MCP Flow (HTTP JSON-RPC)
1. Client calls `POST /mcp` with method `tools/list`.
2. Server returns registered tool metadata + input schemas.
3. Client calls `POST /mcp` with method `tools/call`.
4. Server validates request and executes matching tool.
5. Response is returned in JSON-RPC result format.

Example request:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
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

## A2A Flow (Discovery + Task API)
1. Agent A fetches `GET /.well-known/agent.json` from Agent B.
2. Agent A reads capabilities and endpoint references.
3. Agent A creates work with `POST /a2a/tasks` (`action=call_tool`).
4. Agent A polls `GET /a2a/tasks/{task_id}` for status/result.

Example task create:
```json
{
  "action": "call_tool",
  "tool_name": "portfolio_tracker",
  "arguments": {
    "default_exchange": "NSE",
    "holdings": [
      {"symbol": "INFY", "quantity": 10, "average_buy_price": 1450}
    ]
  },
  "requester": "portfolio-orchestrator-agent"
}
```

## Why both MCP and A2A
- MCP answers: "How does a client invoke tools on this server?"
- A2A answers: "How do agents discover each other and delegate tasks?"
- Together they enable:
  - deterministic tool calls (MCP),
  - multi-agent orchestration (A2A),
  - transport flexibility (HTTP JSON-RPC and stdio MCP SDK).

## Validation and Error Handling
- `/mcp` requests use request models and JSON-RPC validation.
- Invalid tool params return JSON-RPC error `-32602`.
- `/a2a/tasks` payloads are validated before execution.
- Task lifecycle status:
  - `running`
  - `completed`
  - `failed`

## Runbook
### HTTP mode
```powershell
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### MCP stdio mode
```powershell
python mcp_stdio_server.py
```

### Smoke test
```powershell
python scripts/mcp_smoke_test.py --base-url http://127.0.0.1:8000
```

## Suggested Production Next Steps
1. Persist A2A tasks in Redis/Postgres (current in-memory store resets on restart).
2. Add auth for `/mcp` and `/a2a/tasks`.
3. Add retry/timeouts and queueing for long-running tools.
4. Add request IDs and structured logs for traceability.
5. Add integration tests for end-to-end MCP + A2A workflows.
