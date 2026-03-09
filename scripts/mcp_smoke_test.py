"""Simple MCP HTTP smoke test client.

Run this while the server is running:
    python scripts/mcp_smoke_test.py --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP HTTP smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Server base URL")
    args = parser.parse_args()

    mcp_url = f"{args.base_url.rstrip('/')}/mcp"

    try:
        tools_list = post_json(
            mcp_url,
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
    except urllib.error.URLError as exc:
        print(f"FAIL: unable to connect to {mcp_url}: {exc}")
        return 1

    tools = tools_list.get("result", {}).get("tools", [])
    tool_names = {tool.get("name") for tool in tools}
    expected_tools = {"health_check", "stock_fundamentals", "earnings_analyzer", "portfolio_tracker"}
    missing = expected_tools - tool_names
    if missing:
        print(f"FAIL: missing tools in tools/list: {sorted(missing)}")
        print(json.dumps(tools_list, indent=2))
        return 1

    health_call = post_json(
        mcp_url,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "health_check", "arguments": {}},
        },
    )

    if "error" in health_call:
        print("FAIL: health_check returned error")
        print(json.dumps(health_call, indent=2))
        return 1

    print("PASS: tools/list and tools/call(health_check) are working.")
    print("Discovered tools:", ", ".join(sorted(tool_names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
