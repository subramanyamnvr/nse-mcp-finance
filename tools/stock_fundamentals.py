"""Stock fundamentals tool (Module 2)."""

from __future__ import annotations

from typing import Any


def _normalize_symbol(symbol: str, exchange: str = "NSE") -> str:
    cleaned = symbol.strip().upper()
    if "." in cleaned:
        return cleaned
    if exchange.upper() == "NSE":
        return f"{cleaned}.NS"
    return cleaned


def get_stock_fundamentals(symbol: str, exchange: str = "NSE") -> dict[str, Any]:
    """
    Fetch stock fundamentals using yfinance.

    Returns a compact payload so MCP clients can consume it easily.
    """
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Missing dependency: yfinance. Install with `pip install yfinance`.") from exc

    ticker_symbol = _normalize_symbol(symbol=symbol, exchange=exchange)
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info or {}

    if not info:
        raise ValueError(f"No data found for symbol '{ticker_symbol}'.")

    return {
        "symbol": ticker_symbol,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "current_price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "source": "yfinance",
    }
