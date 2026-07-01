#!/usr/bin/env python3
"""
Competitive Positioning Helper Script

Benchmarks a stock against sector averages and summarizes its market position
(share, rank, strengths, weaknesses, trends). This replaces the previous
in-process competitive custom tools with a skill-driven helper script.
"""

import argparse
import json
import sys
from pathlib import Path

# (label, key, higher_is_better)
BENCHMARK_METRICS = [
    ("P/E Ratio", "pe_ratio", False),
    ("Profit Margin (%)", "profit_margin", True),
    ("ROE (%)", "roe", True),
    ("Revenue Growth (%)", "revenue_growth", True),
]


def sector_benchmark(ticker: str, stock: dict, sector: dict, sector_name: str):
    """Compare a stock's metrics against sector averages."""
    lines = [
        f"Sector Benchmark Analysis: {ticker}",
        f"Sector: {sector_name}",
        "=" * 50,
        "",
    ]
    better = worse = 0

    for label, key, higher_is_better in BENCHMARK_METRICS:
        stock_value = stock.get(key, 0)
        sector_value = sector.get(key, 0)
        if not stock_value or not sector_value:
            continue

        lines.append(f"{label}:")
        lines.append(f"  {ticker}: {stock_value:.2f}")
        lines.append(f"  Sector Avg: {sector_value:.2f}")

        is_better = stock_value > sector_value if higher_is_better else stock_value < sector_value
        diff_pct = abs((stock_value - sector_value) / sector_value * 100)
        if is_better:
            lines.append(f"  Outperforms sector by {diff_pct:.1f}%")
            better += 1
        else:
            lines.append(f"  Underperforms sector by {diff_pct:.1f}%")
            worse += 1
        lines.append("")

    total = better + worse
    verdict = None
    if total:
        if better > worse:
            verdict = "Sector Leader"
            lines.append(f"Competitive Position: {verdict} (outperforms on {better}/{total} metrics)")
        elif worse > better:
            verdict = "Sector Laggard"
            lines.append(f"Competitive Position: {verdict} (underperforms on {worse}/{total} metrics)")
        else:
            verdict = "Sector Average"
            lines.append(f"Competitive Position: {verdict}")

    return verdict, "\n".join(lines).rstrip()


def market_position(ticker: str, data: dict) -> str:
    """Summarize market share, rank, strengths, weaknesses, and trends."""
    market_share = data.get("market_share", 0)
    rank = data.get("rank", 0)
    total_competitors = data.get("total_competitors", 0)
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])
    trends = data.get("market_trends", [])

    lines = [f"Market Position Analysis: {ticker}", "=" * 50, ""]
    lines.append(f"Market Share: {market_share:.1f}%")
    if market_share > 25:
        lines.append("  Market Leader")
    elif market_share > 15:
        lines.append("  Strong Position")
    elif market_share > 5:
        lines.append("  Moderate Position")
    else:
        lines.append("  Niche Player")
    lines.append("")
    lines.append(f"Market Rank: #{rank} of {total_competitors} major competitors")
    lines.append("")

    if strengths:
        lines.append("Competitive Strengths:")
        lines.extend(f"  - {s}" for s in strengths)
        lines.append("")
    if weaknesses:
        lines.append("Competitive Weaknesses:")
        lines.extend(f"  - {w}" for w in weaknesses)
        lines.append("")
    if trends:
        lines.append("Relevant Market Trends:")
        lines.extend(f"  - {t}" for t in trends)
        lines.append("")

    lines.append("Strategic Assessment:")
    if market_share > 20 and len(strengths) > len(weaknesses):
        lines.append("  Strong competitive position with sustainable advantages.")
    elif market_share > 10:
        lines.append("  Solid position but facing competitive pressure.")
    else:
        lines.append("  Challenging position requiring strategic repositioning.")

    return "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark a stock against its sector and summarize market position"
    )
    parser.add_argument("--input", required=True, help="Path to JSON file with benchmark and position data")
    parser.add_argument("--output", help="Optional path to write JSON results")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: could not read JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    ticker = data.get("ticker", "Unknown")
    sections = []
    verdict = None

    stock = data.get("stock", {})
    sector = data.get("sector_avg", {})
    if stock and sector:
        verdict, benchmark_text = sector_benchmark(
            ticker, stock, sector, data.get("sector_name", "Unknown Sector")
        )
        sections.append(benchmark_text)

    if "market_share" in data or data.get("strengths") or data.get("weaknesses"):
        sections.append(market_position(ticker, data))

    if not sections:
        print(
            "ERROR: input must include 'stock'/'sector_avg' or market position fields",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\n\n".join(sections))

    if args.output:
        result = {"ticker": ticker}
        if verdict:
            result["competitive_position"] = verdict
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(f"\nResults written to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
