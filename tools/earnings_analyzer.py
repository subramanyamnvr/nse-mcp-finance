"""Earnings analyzer tool (Module 3)."""

from __future__ import annotations

from datetime import date
from typing import Any

def _normalize_symbol(symbol: str, exchange: str = "NSE") -> str:
    cleaned = symbol.strip().upper()
    if "." in cleaned:
        return cleaned
    if exchange.upper() == "NSE":
        return f"{cleaned}.NS"
    return cleaned


def _extract_next_earnings_date(earnings_dates: Any) -> str | None:
    if earnings_dates is None or earnings_dates.empty:
        return None

    for idx in earnings_dates.index:
        if hasattr(idx, "date"):
            candidate = idx.date()
        elif isinstance(idx, date):
            candidate = idx
        else:
            continue
        if candidate >= date.today():
            return candidate.isoformat()
    return None


def get_earnings_analysis(symbol: str, exchange: str = "NSE") -> dict[str, Any]:
    """
    Return compact earnings-oriented metrics for MCP responses.
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

    earnings_dates = ticker.get_earnings_dates(limit=8)
    next_earnings_date = _extract_next_earnings_date(earnings_dates)

    return {
        "symbol": ticker_symbol,
        "name": info.get("longName"),
        "currency": info.get("currency"),
        "next_earnings_date": next_earnings_date,
        "trailing_eps": info.get("trailingEps"),
        "forward_eps": info.get("forwardEps"),
        "earnings_growth": info.get("earningsGrowth"),
        "peg_ratio": info.get("pegRatio"),
        "recommendation": info.get("recommendationKey"),
        "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
        "source": "yfinance",
    }
