---
name: stock-lookup
description: Fetch and analyze historical stock data for any ticker symbol. Use when the user asks to "look up", "fetch", "get data for", or "analyze" a specific stock ticker. Retrieves price history, volume, and basic statistics.
---

# Stock Data Lookup Skill

## Purpose
This skill fetches historical stock market data for any ticker symbol using yfinance. It provides price history, trading volume, and basic statistics.

## When to Use
Use this skill when the user:
- Asks to analyze a specific stock (e.g., "analyze AAPL", "look up Tesla stock")
- Wants historical data for a ticker
- Needs current or recent stock prices
- Requests trading volume information

## Capabilities
- Fetch historical stock data (any time period)
- Get current stock price
- Calculate basic statistics (mean, min, max, volatility)
- Export data to JSON or CSV format

## Workflow

### 1. Identify the Ticker Symbol
Extract the ticker symbol from the user's request (e.g., "AAPL", "TSLA", "MSFT").

### 2. Determine Time Period
Default to the last 6 months unless the user specifies otherwise:
- "last month" → 1 month
- "last year" → 12 months
- "YTD" → year to date
- "last 3 months" → 3 months

### 3. Use the Helper Script
There's a helper script `fetch_stock.py` in this skill directory that you can use:

```bash
uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output tmp/aapl_data.json
```

**Arguments**:
- `--ticker` (required): Stock ticker symbol
- `--period` (optional): Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max). Default: 6mo
- `--output` (required): Output file path (use absolute path in tmp/)
- `--format` (optional): Output format (json or csv). Default: json

### 4. Analyze the Results
After fetching data, read the output file and provide insights:
- Current price vs. historical average
- Price trend (up/down/sideways)
- Volatility level (high/moderate/low)
- Trading volume patterns

## Output Format

The helper script returns JSON with this structure:
```json
{
  "ticker": "AAPL",
  "period": "6mo",
  "data_points": 125,
  "date_range": {
    "start": "2025-08-01",
    "end": "2026-02-03"
  },
  "current_price": 270.01,
  "statistics": {
    "mean": 268.72,
    "min": 246.70,
    "max": 286.19,
    "std_dev": 9.45,
    "volatility_pct": 3.52
  },
  "history": [
    {"date": "2025-08-01", "open": 269.88, "high": 271.23, "low": 268.12, "close": 270.15, "volume": 45234100},
    ...
  ]
}
```

## Example Usage

**User**: "Look up Apple stock for the last year"

**Agent Workflow**:
1. Identify ticker: AAPL
2. Identify period: 1y
3. Run: `uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 1y --output tmp/aapl_1y.json`
4. Read the output file
5. Provide analysis based on the data

## Important Notes
- Always use absolute paths for output files (in the tmp/ directory)
- The script requires yfinance package (already installed via uv)
- If the ticker is invalid, the script will return an error
- Use `uv run python` to execute the script (not plain `python`)
