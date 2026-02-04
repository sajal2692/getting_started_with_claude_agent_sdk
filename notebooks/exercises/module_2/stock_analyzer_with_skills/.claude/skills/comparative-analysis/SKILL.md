---
name: comparative-analysis
description: Compare performance of multiple stocks side-by-side. Use when the user asks to "compare", "contrast", "which is better", or analyze "multiple stocks" together. Calculates returns, volatility, and correlations.
---

# Comparative Stock Analysis Skill

## Purpose
This skill compares the performance of multiple stocks over the same time period, providing side-by-side metrics to help with investment decisions.

## When to Use
Use this skill when the user:
- Asks to compare multiple stocks (e.g., "compare AAPL and MSFT")
- Wants to know which stock performed better
- Needs correlation analysis between stocks
- Requests sector or peer comparison

## Capabilities
- Compare 2-10 stocks simultaneously
- Calculate returns for each stock
- Measure relative volatility
- Compute correlation coefficients
- Identify best/worst performers
- Generate comparison tables

## Workflow

### 1. Identify Ticker Symbols
Extract all ticker symbols from the user's request:
- "Compare Apple and Microsoft" → AAPL, MSFT
- "How do TSLA, RIVN, and LCID compare?" → TSLA, RIVN, LCID

### 2. Determine Time Period
Use the same period for all stocks to ensure fair comparison:
- Default: 6 months
- Match user's specification: "last year", "YTD", "last 3 months"

### 3. Use the Helper Script
The helper script `compare_stocks.py` handles multi-stock comparison:

```bash
uv run python .claude/skills/comparative-analysis/compare_stocks.py \
  --tickers AAPL MSFT GOOGL \
  --period 6mo \
  --output tmp/comparison_results.json
```

**Arguments**:
- `--tickers` (required): Space-separated list of ticker symbols
- `--period` (optional): Time period (1mo, 3mo, 6mo, 1y, 2y, 5y). Default: 6mo
- `--output` (required): Output file path (use absolute path in tmp/)
- `--benchmark` (optional): Benchmark ticker for comparison (e.g., SPY for S&P 500)

### 4. Analyze the Results
After running the comparison, interpret the results:
- Identify the top performer (highest return)
- Note the most/least volatile stock
- Explain correlation patterns (diversification potential)
- Provide investment insights based on the metrics

## Output Format

The helper script returns JSON with this structure:
```json
{
  "comparison_date": "2026-02-03",
  "period": "6mo",
  "date_range": {
    "start": "2025-08-03",
    "end": "2026-02-03"
  },
  "stocks": [
    {
      "ticker": "AAPL",
      "start_price": 219.57,
      "end_price": 270.01,
      "total_return_pct": 22.97,
      "annualized_return_pct": 45.02,
      "volatility_pct": 21.46,
      "sharpe_ratio": 2.10,
      "max_drawdown_pct": -8.54
    },
    {
      "ticker": "MSFT",
      "start_price": 519.01,
      "end_price": 423.37,
      "total_return_pct": -18.43,
      "annualized_return_pct": -39.25,
      "volatility_pct": 23.39,
      "sharpe_ratio": -1.68,
      "max_drawdown_pct": -22.12
    }
  ],
  "correlations": {
    "AAPL_MSFT": 0.085,
    "AAPL_GOOGL": 0.421,
    "MSFT_GOOGL": 0.060
  },
  "rankings": {
    "best_return": "AAPL",
    "worst_return": "MSFT",
    "most_volatile": "MSFT",
    "least_volatile": "AAPL",
    "best_risk_adjusted": "AAPL"
  }
}
```

## Interpretation Guidelines

### Returns
- **Total Return**: Overall percentage gain/loss over the period
- **Annualized Return**: Extrapolated annual rate (useful for comparing different periods)
- Compare returns to benchmark (e.g., S&P 500) to assess relative performance

### Volatility
- **Volatility %**: Standard deviation of returns (higher = more risky)
- Lower volatility is generally preferred for risk-averse investors
- High volatility stocks may offer higher returns but with more risk

### Risk-Adjusted Metrics
- **Sharpe Ratio**: Return per unit of risk (higher is better)
  - < 1.0: Poor risk-adjusted performance
  - 1.0-2.0: Good
  - > 2.0: Excellent
- **Max Drawdown**: Largest peak-to-trough decline (risk measure)

### Correlation
- **< 0.3**: Low correlation (good for diversification)
- **0.3-0.7**: Moderate correlation
- **> 0.7**: High correlation (less diversification benefit)

## Example Usage

**User**: "Compare Tesla, Ford, and GM stock performance over the last year"

**Agent Workflow**:
1. Identify tickers: TSLA, F, GM
2. Period: 1y
3. Run: `uv run python .claude/skills/comparative-analysis/compare_stocks.py --tickers TSLA F GM --period 1y --output tmp/ev_comparison.json`
4. Read the results
5. Provide interpretation:
   - Which stock had the best return?
   - Which is most volatile?
   - Are they correlated (move together)?
   - Investment implications

## Important Notes
- All stocks must have data for the same time period
- Use absolute paths for output files (in tmp/)
- Invalid tickers will cause the script to fail
- Correlations require at least 2 stocks
- Use `uv run python` to execute (not plain `python`)
