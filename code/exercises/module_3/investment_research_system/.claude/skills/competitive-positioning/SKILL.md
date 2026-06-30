---
name: competitive-positioning
description: Benchmark a stock against sector averages and assess its market position, share, and competitive advantages. Use when you need to understand a company's competitive landscape, peer ranking, or sector standing.
---

# Competitive Positioning Skill

## Purpose
This skill places a company in its competitive context. It benchmarks key metrics
against sector averages and summarizes market share, peer ranking, strengths,
weaknesses, and relevant trends into a clear positioning read.

## When to Use
Use this skill when the user (or a coordinating agent):
- Wants to compare a company against its sector or peers
- Asks about market share, competitive advantages, or rank
- Needs a sector-leader vs. laggard assessment

> Note: This is distinct from the `comparative-analysis` skill, which compares the
> *price performance* of multiple tickers. Use `competitive-positioning` for
> sector benchmarking and qualitative market position.

## Capabilities
- Benchmark P/E, profit margin, ROE, and revenue growth against sector averages
- Classify competitive position (Sector Leader / Average / Laggard)
- Summarize market share, rank, strengths, weaknesses, and trends
- Optionally export results to JSON

## Workflow

### 1. Assemble the Inputs
Gather the company's metrics, the sector averages, and qualitative position data.
Write them to a JSON file in `tmp/`. Each block is optional: supply the benchmark
block, the market-position block, or both.

Example `tmp/competitive.json`:
```json
{
  "ticker": "AAPL",
  "sector_name": "Technology",
  "stock": { "pe_ratio": 30.0, "profit_margin": 25.0, "roe": 150.0, "revenue_growth": 8.0 },
  "sector_avg": { "pe_ratio": 28.0, "profit_margin": 15.0, "roe": 35.0, "revenue_growth": 10.0 },
  "market_share": 28.0,
  "rank": 1,
  "total_competitors": 5,
  "strengths": ["Brand loyalty", "Ecosystem", "Pricing power"],
  "weaknesses": ["iPhone dependence"],
  "market_trends": ["AI on device", "Services growth"]
}
```

### 2. Run the Helper Script
```bash
uv run python .claude/skills/competitive-positioning/benchmark.py \
  --input tmp/competitive.json \
  --output tmp/competitive_out.json
```

**Arguments**:
- `--input` (required): Path to a JSON file with benchmark and/or position data
- `--output` (optional): Path to write JSON results (e.g., `tmp/competitive_out.json`)

### 3. Interpret the Results
- **Sector Leader**: outperforms on a majority of benchmarked metrics
- **Market share**: > 25% leader, 15-25% strong, 5-15% moderate, < 5% niche
- Combine the quantitative benchmark with the qualitative strengths/weaknesses to
  explain *why* the company holds its position

## Output Format

When `--output` is supplied, the script writes JSON like:
```json
{
  "ticker": "AAPL",
  "competitive_position": "Sector Leader"
}
```

## Important Notes
- Sector averages and qualitative inputs are supplied by you, not fetched live
- For P/E, lower than the sector counts as outperforming; for margins/ROE/growth, higher is better
- Use absolute paths under `tmp/` for input/output files
- Use `uv run python` to execute (not plain `python`)
