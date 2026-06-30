---
name: financial-analysis
description: Calculate fundamental financial metrics (P/E, ROE, profit margin, market cap) and assess valuation as overvalued, fairly valued, or undervalued. Use when you need deep financial analysis of a company's fundamentals.
---

# Financial Analysis Skill

## Purpose
This skill turns raw financial figures into fundamental metrics and a valuation
verdict. It computes P/E, profit margin, ROE, and market cap, and weighs P/E,
PEG, and P/B against industry norms to judge whether a stock is overvalued,
fairly valued, or undervalued.

## When to Use
Use this skill when the user (or a coordinating agent):
- Asks for fundamental analysis, financial metrics, or ratios
- Wants a valuation assessment ("is it overvalued?")
- Needs profitability or financial-health indicators (P/E, ROE, margins)

## Capabilities
- Compute P/E ratio, profit margin, ROE, and market capitalization
- Categorize market cap (Mega / Large / Mid / Small)
- Assess valuation from P/E, PEG, and P/B against an industry average
- Optionally export results to JSON

## Workflow

### 1. Gather the Inputs
Collect the financial figures you have for the company. Use the `stock-lookup`
skill for price data, then supply the fundamental figures you know. Write them to
a JSON file in `tmp/`. Any fields you omit are simply skipped.

Example `tmp/financials.json`:
```json
{
  "ticker": "AAPL",
  "price": 195.0,
  "earnings_per_share": 6.4,
  "revenue": 383000000000,
  "net_income": 97000000000,
  "shareholders_equity": 62000000000,
  "shares_outstanding": 15500000000,
  "peg_ratio": 2.1,
  "pb_ratio": 45.0,
  "industry_avg_pe": 28.0
}
```

### 2. Run the Helper Script
```bash
uv run python .claude/skills/financial-analysis/compute_metrics.py \
  --input tmp/financials.json \
  --output tmp/metrics.json
```

**Arguments**:
- `--input` (required): Path to a JSON file with financial figures
- `--output` (optional): Path to write JSON results (e.g., `tmp/metrics.json`)

The script computes metrics from any raw figures present (price, EPS, revenue,
etc.) and assesses valuation from any ratios present. P/E is derived from
price / EPS when not supplied directly.

### 3. Interpret the Results
- **P/E**: < 15 cheap, 15-30 reasonable, > 30 rich (or high-growth)
- **Profit margin**: > 20% excellent, 10-20% good, < 10% low
- **ROE**: > 20% excellent, 15-20% good, < 15% moderate
- **Valuation**: majority of P/E, PEG, P/B signals decides over/fair/undervalued

## Output Format

When `--output` is supplied, the script writes JSON like:
```json
{
  "ticker": "AAPL",
  "metrics": {
    "pe_ratio": 30.47,
    "profit_margin_pct": 25.33,
    "roe_pct": 156.45,
    "market_cap": 3022500000000
  },
  "valuation": "Overvalued"
}
```

## Important Notes
- Inputs are supplied figures, not live fundamentals; provide your best data
- Valuation requires at least one of P/E, PEG, or P/B to produce a verdict
- Use absolute paths under `tmp/` for input/output files
- Use `uv run python` to execute (not plain `python`)
