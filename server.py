"""
Module 1: Server bootstrap + A2A discovery card.

This is intentionally small and incremental:
- Provides a health endpoint for deployment checks.
- Publishes an A2A-style agent card so other agents can discover capabilities.
- Adds a minimal MCP-style JSON-RPC endpoint with tool registry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from tools.earnings_analyzer import get_earnings_analysis
from tools.portfolio_tracker import analyze_portfolio
from tools.stock_fundamentals import get_stock_fundamentals


app = FastAPI(
    title="mcp-finance-server",
    description="Incremental MCP finance server with A2A discovery.",
    version="0.5.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "mcp-finance-server"}


@app.get("/.well-known/agent.json")
def agent_card() -> dict:
    """
    A2A discovery document.
    Kept simple for first module so it can be expanded later with auth and skills.
    """
    return {
        "name": "MCP Finance Agent",
        "description": "Finance-focused MCP server with agent-to-agent discoverability.",
        "version": "0.1.0",
        "protocols": ["mcp", "a2a"],
        "capabilities": {
            "tools": [
                {
                    "name": "health_check",
                    "description": "Returns server health status.",
                    "input_schema": {"type": "object", "properties": {}},
                },
                {
                    "name": "stock_fundamentals",
                    "description": "Returns compact stock fundamentals for a symbol.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "exchange": {"type": "string", "default": "NSE"},
                        },
                        "required": ["symbol"],
                    },
                },
                {
                    "name": "earnings_analyzer",
                    "description": "Returns earnings-focused metrics for a symbol.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "exchange": {"type": "string", "default": "NSE"},
                        },
                        "required": ["symbol"],
                    },
                },
                {
                    "name": "portfolio_tracker",
                    "description": "Returns current valuation and P/L for provided holdings.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "holdings": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "average_buy_price": {"type": "number"},
                                        "exchange": {"type": "string", "default": "NSE"},
                                    },
                                    "required": ["symbol", "quantity"],
                                },
                            },
                            "default_exchange": {"type": "string", "default": "NSE"},
                        },
                        "required": ["holdings"],
                    },
                }
            ],
            "planned_tools": [],
        },
        "endpoints": {
            "health": "/health",
            "agent_card": "/.well-known/agent.json",
            "mcp": "/mcp",
            "a2a_tasks": "/a2a/tasks",
        },
    }


TOOLS: dict[str, dict[str, Any]] = {
    "health_check": {
        "description": "Returns server health status.",
        "input_schema": {"type": "object", "properties": {}},
    },
    "stock_fundamentals": {
        "description": "Returns compact stock fundamentals for a symbol.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "exchange": {"type": "string", "default": "NSE"},
            },
            "required": ["symbol"],
        },
    },
    "earnings_analyzer": {
        "description": "Returns earnings-focused metrics for a symbol.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "exchange": {"type": "string", "default": "NSE"},
            },
            "required": ["symbol"],
        },
    },
    "portfolio_tracker": {
        "description": "Returns current valuation and P/L for provided holdings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "holdings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "quantity": {"type": "number"},
                            "average_buy_price": {"type": "number"},
                            "exchange": {"type": "string", "default": "NSE"},
                        },
                        "required": ["symbol", "quantity"],
                    },
                },
                "default_exchange": {"type": "string", "default": "NSE"},
            },
            "required": ["holdings"],
        },
    },
}


def _tool_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "mcp-finance-server"}


def _tool_stock_fundamentals(arguments: dict[str, Any]) -> dict[str, Any]:
    symbol = arguments.get("symbol")
    exchange = arguments.get("exchange", "NSE")
    if not symbol:
        raise ValueError("Missing required argument: symbol")
    return get_stock_fundamentals(symbol=symbol, exchange=exchange)


def _tool_earnings_analyzer(arguments: dict[str, Any]) -> dict[str, Any]:
    symbol = arguments.get("symbol")
    exchange = arguments.get("exchange", "NSE")
    if not symbol:
        raise ValueError("Missing required argument: symbol")
    return get_earnings_analysis(symbol=symbol, exchange=exchange)


def _tool_portfolio_tracker(arguments: dict[str, Any]) -> dict[str, Any]:
    holdings = arguments.get("holdings")
    default_exchange = arguments.get("default_exchange", "NSE")
    if holdings is None:
        raise ValueError("Missing required argument: holdings")
    if not isinstance(holdings, list):
        raise ValueError("holdings must be an array")
    return analyze_portfolio(holdings=holdings, default_exchange=default_exchange)


def _mcp_success(response_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": response_id, "result": result}


def _mcp_error(response_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": response_id, "error": {"code": code, "message": message}}


def _execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "health_check":
        return _tool_health_check()
    if tool_name == "stock_fundamentals":
        return _tool_stock_fundamentals(arguments)
    if tool_name == "earnings_analyzer":
        return _tool_earnings_analyzer(arguments)
    if tool_name == "portfolio_tracker":
        return _tool_portfolio_tracker(arguments)
    raise ValueError(f"Tool not found: {tool_name}")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


A2A_TASKS: dict[str, dict[str, Any]] = {}


@app.post("/mcp")
def mcp_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal JSON-RPC endpoint with MCP-style methods:
    - tools/list
    - tools/call
    """
    if payload.get("jsonrpc") != "2.0":
        raise HTTPException(status_code=400, detail="Invalid JSON-RPC version.")

    method = payload.get("method")
    params = payload.get("params", {})
    request_id = payload.get("id")

    if method == "tools/list":
        result = {
            "tools": [
                {"name": name, "description": meta["description"], "input_schema": meta["input_schema"]}
                for name, meta in TOOLS.items()
            ]
        }
        return _mcp_success(request_id, result)

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            result = _execute_tool(tool_name=tool_name, arguments=arguments)
            return _mcp_success(request_id, {"content": [{"type": "json", "json": result}]})
        except Exception as exc:
            return _mcp_error(request_id, -32000, str(exc))

    return _mcp_error(request_id, -32601, f"Method not found: {method}")


@app.post("/a2a/tasks")
def create_a2a_task(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Create an A2A task that requests this agent to execute one tool.

    Payload:
    {
      "action": "call_tool",
      "tool_name": "stock_fundamentals",
      "arguments": {"symbol": "INFY", "exchange": "NSE"},
      "requester": "agent-name-optional"
    }
    """
    action = payload.get("action")
    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments", {})
    requester = payload.get("requester")

    if action != "call_tool":
        raise HTTPException(status_code=400, detail="Unsupported action. Use 'call_tool'.")
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing required field: tool_name")

    task_id = str(uuid4())
    task = {
        "task_id": task_id,
        "status": "running",
        "action": action,
        "tool_name": tool_name,
        "arguments": arguments,
        "requester": requester,
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
        "result": None,
        "error": None,
    }
    A2A_TASKS[task_id] = task

    try:
        result = _execute_tool(tool_name=tool_name, arguments=arguments)
        task["result"] = result
        task["status"] = "completed"
    except Exception as exc:
        task["error"] = str(exc)
        task["status"] = "failed"
    task["updated_at"] = _utc_now_iso()

    return {
        "task_id": task_id,
        "status": task["status"],
        "poll_url": f"/a2a/tasks/{task_id}",
    }


@app.get("/a2a/tasks/{task_id}")
def get_a2a_task(task_id: str) -> dict[str, Any]:
    task = A2A_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return task
