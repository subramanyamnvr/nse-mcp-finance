"""Official MCP SDK server entrypoint (stdio transport).

This module is separate from the FastAPI HTTP app so both modes can coexist:
- HTTP mode (`server.py`) for web/API demos
- MCP SDK stdio mode (`mcp_stdio_server.py`) for MCP-native clients
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from tools.earnings_analyzer import get_earnings_analysis
from tools.portfolio_tracker import analyze_portfolio
from tools.stock_fundamentals import get_stock_fundamentals


mcp = FastMCP("nse-mcp-finance")


@mcp.tool()
def health_check() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok", "service": "nse-mcp-finance"}


@mcp.tool()
def stock_fundamentals(symbol: str, exchange: str = "NSE") -> dict[str, Any]:
    """Return compact stock fundamentals for a symbol."""
    return get_stock_fundamentals(symbol=symbol, exchange=exchange)


@mcp.tool()
def earnings_analyzer(symbol: str, exchange: str = "NSE") -> dict[str, Any]:
    """Return earnings-focused metrics for a symbol."""
    return get_earnings_analysis(symbol=symbol, exchange=exchange)


@mcp.tool()
def portfolio_tracker(holdings: list[dict[str, Any]], default_exchange: str = "NSE") -> dict[str, Any]:
    """Return position-level and total portfolio valuation/P&L."""
    return analyze_portfolio(holdings=holdings, default_exchange=default_exchange)


if __name__ == "__main__":
    mcp.run()
