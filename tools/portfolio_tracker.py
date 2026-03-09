"""Portfolio tracker tool (Module 4)."""

from __future__ import annotations

from typing import Any


def _normalize_symbol(symbol: str, exchange: str = "NSE") -> str:
    cleaned = symbol.strip().upper()
    if "." in cleaned:
        return cleaned
    if exchange.upper() == "NSE":
        return f"{cleaned}.NS"
    return cleaned


def _latest_price(ticker: Any) -> float:
    # Try fast path first, then fallback to 1d history.
    fast = getattr(ticker, "fast_info", None) or {}
    for key in ("lastPrice", "last_price", "regularMarketPrice"):
        value = fast.get(key)
        if value is not None:
            return float(value)

    hist = ticker.history(period="1d")
    if hist is None or hist.empty:
        raise ValueError("Unable to fetch latest market price.")
    return float(hist["Close"].iloc[-1])


def analyze_portfolio(holdings: list[dict[str, Any]], default_exchange: str = "NSE") -> dict[str, Any]:
    """
    Analyze a portfolio.

    Input holding schema:
    - symbol: str (required)
    - quantity: float (required)
    - average_buy_price: float (optional)
    - exchange: str (optional, defaults to default_exchange)
    """
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Missing dependency: yfinance. Install with `pip install yfinance`.") from exc

    if not holdings:
        raise ValueError("holdings must contain at least one position.")

    positions: list[dict[str, Any]] = []
    total_invested = 0.0
    total_current_value = 0.0

    for idx, holding in enumerate(holdings, start=1):
        symbol = holding.get("symbol")
        quantity = holding.get("quantity")
        avg_buy = holding.get("average_buy_price")
        exchange = holding.get("exchange", default_exchange)

        if not symbol:
            raise ValueError(f"holdings[{idx}] missing symbol")
        if quantity is None:
            raise ValueError(f"holdings[{idx}] missing quantity")

        quantity = float(quantity)
        ticker_symbol = _normalize_symbol(symbol=symbol, exchange=exchange)
        ticker = yf.Ticker(ticker_symbol)
        current_price = _latest_price(ticker)
        current_value = quantity * current_price

        invested = None
        pnl = None
        pnl_percent = None
        if avg_buy is not None:
            invested = quantity * float(avg_buy)
            pnl = current_value - invested
            pnl_percent = (pnl / invested * 100.0) if invested else None
            total_invested += invested

        total_current_value += current_value

        positions.append(
            {
                "symbol": ticker_symbol,
                "quantity": quantity,
                "current_price": current_price,
                "current_value": current_value,
                "average_buy_price": avg_buy,
                "invested": invested,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
            }
        )

    portfolio_pnl = None
    portfolio_pnl_percent = None
    if total_invested > 0:
        portfolio_pnl = total_current_value - total_invested
        portfolio_pnl_percent = (portfolio_pnl / total_invested) * 100.0

    return {
        "positions": positions,
        "totals": {
            "positions_count": len(positions),
            "invested": total_invested if total_invested > 0 else None,
            "current_value": total_current_value,
            "pnl": portfolio_pnl,
            "pnl_percent": portfolio_pnl_percent,
        },
        "source": "yfinance",
    }
