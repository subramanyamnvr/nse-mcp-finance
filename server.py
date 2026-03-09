"""
Module 1: Server bootstrap + A2A discovery card.

This is intentionally small and incremental:
- Provides a health endpoint for deployment checks.
- Publishes an A2A-style agent card so other agents can discover capabilities.
- Adds a minimal MCP-style JSON-RPC endpoint with tool registry.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from tools.earnings_analyzer import get_earnings_analysis
from tools.stock_fundamentals import get_stock_fundamentals


app = FastAPI(
    title="mcp-finance-server",
    description="Incremental MCP finance server with A2A discovery.",
    version="0.3.0",
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
                }
            ],
            "planned_tools": [
                "portfolio_tracker",
            ],
        },
        "endpoints": {
            "health": "/health",
            "agent_card": "/.well-known/agent.json",
            "mcp": "/mcp",
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


def _mcp_success(response_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": response_id, "result": result}


def _mcp_error(response_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": response_id, "error": {"code": code, "message": message}}


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
            if tool_name == "health_check":
                return _mcp_success(request_id, {"content": [{"type": "json", "json": _tool_health_check()}]})
            if tool_name == "stock_fundamentals":
                result = _tool_stock_fundamentals(arguments)
                return _mcp_success(request_id, {"content": [{"type": "json", "json": result}]})
            if tool_name == "earnings_analyzer":
                result = _tool_earnings_analyzer(arguments)
                return _mcp_success(request_id, {"content": [{"type": "json", "json": result}]})
        except Exception as exc:
            return _mcp_error(request_id, -32000, str(exc))

        return _mcp_error(request_id, -32601, f"Tool not found: {tool_name}")

    return _mcp_error(request_id, -32601, f"Method not found: {method}")
