# mcp-finance-server

## Overview
Template-only scaffold for an MCP finance tools server.

## Skills Demonstrated
- MCP (Model Context Protocol)
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

## Implementation Plan (To Do)
1. Install MCP SDK (`pip install mcp`)
2. Create MCP server base
3. Build stock fundamentals tool
4. Build earnings analyzer tool
5. Build portfolio tracker tool
6. Register tools with MCP server
7. Add tool schemas
8. Test with MCP client
9. Containerize with Docker
10. Deploy with Cloud Build + Cloud Run
11. Write MCP integration guide

## Business Value
Extends any AI assistant with live Indian market data.

## Tech Stack
- Python MCP SDK
- FastAPI
- Cloud Run
- yfinance/NSE API
- GCP
