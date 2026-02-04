---
name: risk-analysis
description: Analyze investment risk metrics for stocks including volatility, beta, VaR, and downside risk. Use when the user asks about "risk", "volatility", "how safe", "beta", or wants to understand risk profile.
---

# Risk Analysis Skill

## Purpose
This skill performs comprehensive risk analysis on stocks, helping investors understand the risk characteristics and potential downside of their investments.

## When to Use
Use this skill when the user:
- Asks about risk level or safety of a stock
- Wants to understand volatility
- Requests beta calculation (market sensitivity)
- Needs Value at Risk (VaR) analysis
- Asks "how risky is this stock?"
- Wants downside risk metrics

## Capabilities
- Calculate multiple volatility measures
- Compute beta (market correlation)
- Value at Risk (VaR) estimation
- Downside deviation and Sortino ratio
- Maximum drawdown analysis
- Risk categorization (low/medium/high)

## Workflow

### 1. Identify the Stock and Benchmark
- Extract ticker symbol from user's request
- Default benchmark: S&P 500 (ticker: SPY or ^GSPC)
- User can specify alternate benchmark

### 2. Determine Analysis Period
- Default: 1 year (good balance for risk metrics)
- Longer periods (2-5 years) provide more stable estimates
- Shorter periods (3-6 months) capture recent risk changes

### 3. Use the Helper Script
The helper script `analyze_risk.py` performs comprehensive risk analysis:

```bash
uv run python .claude/skills/risk-analysis/analyze_risk.py \
  --ticker TSLA \
  --benchmark ^GSPC \
  --period 1y \
  --confidence 0.95 \
  --output tmp/tsla_risk.json
```

**Arguments**:
- `--ticker` (required): Stock ticker symbol to analyze
- `--benchmark` (optional): Benchmark ticker (default: ^GSPC for S&P 500)
- `--period` (optional): Time period (3mo, 6mo, 1y, 2y, 5y). Default: 1y
- `--confidence` (optional): Confidence level for VaR (0.90, 0.95, 0.99). Default: 0.95
- `--output` (required): Output file path (use absolute path in tmp/)

### 4. Interpret the Results
Provide user-friendly interpretation of risk metrics:

**Volatility**:
- < 15%: Low risk (stable, blue-chip stocks)
- 15-30%: Moderate risk (typical stocks)
- > 30%: High risk (volatile growth stocks, crypto-related)

**Beta**:
- < 0.8: Less volatile than market (defensive)
- 0.8-1.2: Similar to market volatility
- > 1.2: More volatile than market (aggressive)

**Value at Risk (VaR)**:
- Worst expected loss at given confidence level
- Example: "95% VaR of -3.5%" means 95% chance daily loss won't exceed 3.5%

**Sharpe Ratio**:
- < 1: Poor risk-adjusted returns
- 1-2: Good risk-adjusted returns
- > 2: Excellent risk-adjusted returns

**Sortino Ratio**:
- Similar to Sharpe but only penalizes downside volatility
- Higher is better
- More relevant for evaluating downside risk

## Output Format

The helper script returns JSON with this structure:
```json
{
  "ticker": "TSLA",
  "benchmark": "^GSPC",
  "analysis_date": "2026-02-03",
  "period": "1y",
  "price_data": {
    "current_price": 245.32,
    "period_return_pct": 15.67,
    "price_range": {
      "min": 182.45,
      "max": 278.91
    }
  },
  "volatility_metrics": {
    "annualized_volatility_pct": 42.15,
    "downside_deviation_pct": 28.34,
    "volatility_category": "High"
  },
  "market_risk": {
    "beta": 1.85,
    "correlation_with_market": 0.62,
    "beta_interpretation": "85% more volatile than market"
  },
  "value_at_risk": {
    "confidence_level": 0.95,
    "daily_var_pct": -3.45,
    "monthly_var_pct": -12.87,
    "interpretation": "95% confidence that daily loss won't exceed 3.45%"
  },
  "risk_adjusted_metrics": {
    "sharpe_ratio": 0.87,
    "sortino_ratio": 1.23,
    "max_drawdown_pct": -35.42,
    "max_drawdown_date": "2025-08-15"
  },
  "risk_assessment": {
    "overall_risk": "High",
    "risk_factors": [
      "High volatility (42.15%)",
      "Beta significantly above 1 (1.85)",
      "Large maximum drawdown (-35.42%)"
    ],
    "suitable_for": "Aggressive investors with high risk tolerance"
  }
}
```

## Risk Assessment Guidelines

### Overall Risk Classification

**Low Risk** (Suitable for conservative investors):
- Volatility < 15%
- Beta < 0.8
- Max drawdown < 15%
- Example: Utility stocks, treasury bonds

**Moderate Risk** (Suitable for balanced investors):
- Volatility 15-30%
- Beta 0.8-1.2
- Max drawdown 15-30%
- Example: Blue-chip stocks, diversified ETFs

**High Risk** (Suitable for aggressive investors):
- Volatility > 30%
- Beta > 1.2
- Max drawdown > 30%
- Example: Growth stocks, tech startups, crypto-related

### Important Considerations

1. **Time Period Matters**: Risk metrics can change over time
2. **Past ≠ Future**: Historical volatility doesn't guarantee future volatility
3. **Context is Key**: High risk isn't bad if returns justify it (check Sharpe/Sortino)
4. **Diversification**: Portfolio risk < sum of individual stock risks

## Example Usage

**User**: "How risky is Tesla stock?"

**Agent Workflow**:
1. Identify ticker: TSLA
2. Use default benchmark: ^GSPC (S&P 500)
3. Use default period: 1y
4. Run: `uv run python .claude/skills/risk-analysis/analyze_risk.py --ticker TSLA --output tmp/tsla_risk.json`
5. Read and interpret results:
   - "Tesla has HIGH risk with 42% annualized volatility"
   - "It's 85% more volatile than the market (beta 1.85)"
   - "There's a 5% chance of losing more than 3.45% in a single day"
   - "Suitable for aggressive investors comfortable with high volatility"

**User**: "Compare the risk of AAPL vs TSLA"

**Agent Workflow**:
1. Run risk analysis on both stocks
2. Compare key metrics (volatility, beta, VaR, Sharpe ratio)
3. Provide relative risk assessment
4. Recommend based on user's risk tolerance

## Important Notes
- Beta calculation requires benchmark data
- VaR assumes normal distribution (may underestimate tail risk)
- Longer time periods provide more reliable risk estimates
- Always use absolute paths for output files (in tmp/)
- Use `uv run python` to execute (not plain `python`)
