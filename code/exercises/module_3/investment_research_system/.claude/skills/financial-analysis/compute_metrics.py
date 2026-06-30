#!/usr/bin/env python3
"""
Financial Metrics & Valuation Helper Script

Calculates fundamental financial metrics (P/E, profit margin, ROE, market cap)
and provides a valuation assessment from supplied financial figures. This
replaces the previous in-process financial custom tools with a skill-driven
helper script.
"""

import argparse
import json
import sys
from pathlib import Path


def compute_metrics(data: dict) -> dict:
    """Compute core financial metrics from raw figures."""
    price = data.get("price", 0)
    eps = data.get("earnings_per_share", 0)
    revenue = data.get("revenue", 0)
    net_income = data.get("net_income", 0)
    equity = data.get("shareholders_equity", 0)
    shares = data.get("shares_outstanding", 0)

    metrics = {}
    if eps and eps > 0 and price:
        metrics["pe_ratio"] = round(price / eps, 2)
    if revenue and revenue > 0:
        metrics["profit_margin_pct"] = round((net_income / revenue) * 100, 2)
    if equity and equity > 0:
        metrics["roe_pct"] = round((net_income / equity) * 100, 2)
    if price and shares:
        metrics["market_cap"] = price * shares
    return metrics


def metrics_report(ticker: str, metrics: dict) -> str:
    lines = [f"Financial Metrics for {ticker}", "=" * 50, ""]

    pe = metrics.get("pe_ratio")
    if pe is not None:
        lines.append(f"P/E Ratio: {pe:.2f}")
        if pe < 15:
            lines.append("  Interpretation: Potentially undervalued")
        elif pe > 30:
            lines.append("  Interpretation: Potentially overvalued or high growth expected")
        else:
            lines.append("  Interpretation: Reasonably valued")
    else:
        lines.append("P/E Ratio: N/A (negative or zero earnings)")
    lines.append("")

    pm = metrics.get("profit_margin_pct")
    if pm is not None:
        lines.append(f"Profit Margin: {pm:.2f}%")
        if pm > 20:
            lines.append("  Interpretation: Excellent profitability")
        elif pm > 10:
            lines.append("  Interpretation: Good profitability")
        else:
            lines.append("  Interpretation: Low profitability")
        lines.append("")

    roe = metrics.get("roe_pct")
    if roe is not None:
        lines.append(f"ROE (Return on Equity): {roe:.2f}%")
        if roe > 20:
            lines.append("  Interpretation: Excellent returns for shareholders")
        elif roe > 15:
            lines.append("  Interpretation: Good returns for shareholders")
        else:
            lines.append("  Interpretation: Moderate returns for shareholders")
        lines.append("")

    cap = metrics.get("market_cap")
    if cap is not None:
        lines.append(f"Market Capitalization: ${cap:,.0f}")
        if cap > 200_000_000_000:
            lines.append("  Category: Mega Cap")
        elif cap > 10_000_000_000:
            lines.append("  Category: Large Cap")
        elif cap > 2_000_000_000:
            lines.append("  Category: Mid Cap")
        else:
            lines.append("  Category: Small Cap")

    return "\n".join(lines).rstrip()


def assess_valuation(ticker: str, data: dict, derived_pe=None):
    """Assess valuation from ratio inputs; returns (verdict, report_text) or (None, None)."""
    pe = data.get("pe_ratio", derived_pe or 0)
    peg = data.get("peg_ratio", 0)
    pb = data.get("pb_ratio", 0)
    industry_pe = data.get("industry_avg_pe", 20)

    lines = [f"Valuation Assessment for {ticker}", "=" * 50, ""]
    signals = []

    if pe and pe > 0:
        lines.append(f"P/E Ratio: {pe:.2f} (Industry Avg: {industry_pe:.2f})")
        if pe < industry_pe * 0.8:
            signals.append("undervalued")
            lines.append("  Below industry average - potentially undervalued")
        elif pe > industry_pe * 1.2:
            signals.append("overvalued")
            lines.append("  Above industry average - potentially overvalued")
        else:
            signals.append("fair")
            lines.append("  In line with industry average")
        lines.append("")

    if peg and peg > 0:
        lines.append(f"PEG Ratio: {peg:.2f}")
        if peg < 1:
            signals.append("undervalued")
            lines.append("  Below 1.0 - undervalued relative to growth")
        elif peg > 2:
            signals.append("overvalued")
            lines.append("  Above 2.0 - overvalued relative to growth")
        else:
            signals.append("fair")
            lines.append("  Fairly valued relative to growth")
        lines.append("")

    if pb and pb > 0:
        lines.append(f"P/B Ratio: {pb:.2f}")
        if pb < 3:
            signals.append("undervalued")
            lines.append("  Below 3.0 - reasonable book value")
        elif pb > 10:
            signals.append("overvalued")
            lines.append("  Above 10.0 - premium to book value")
        else:
            signals.append("fair")
            lines.append("  Moderate premium to book value")
        lines.append("")

    if not signals:
        return None, None

    overvalued = signals.count("overvalued")
    undervalued = signals.count("undervalued")
    if undervalued > overvalued:
        verdict = "Undervalued"
        lines.append(f"Overall Valuation: {verdict}")
        lines.append(f"Majority of signals ({undervalued}/{len(signals)}) suggest trading below fair value.")
    elif overvalued > undervalued:
        verdict = "Overvalued"
        lines.append(f"Overall Valuation: {verdict}")
        lines.append(f"Majority of signals ({overvalued}/{len(signals)}) suggest trading above fair value.")
    else:
        verdict = "Fairly Valued"
        lines.append(f"Overall Valuation: {verdict}")
        lines.append("Signals are mixed, suggesting trading near fair value.")

    return verdict, "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(
        description="Compute financial metrics and valuation from supplied figures"
    )
    parser.add_argument("--input", required=True, help="Path to JSON file with financial figures")
    parser.add_argument("--output", help="Optional path to write JSON results")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: could not read JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    ticker = data.get("ticker", "Unknown")
    metrics = compute_metrics(data)
    sections = [metrics_report(ticker, metrics)]

    verdict, valuation_text = assess_valuation(ticker, data, derived_pe=metrics.get("pe_ratio"))
    if valuation_text:
        sections.append(valuation_text)

    print("\n\n".join(sections))

    if args.output:
        result = {"ticker": ticker, "metrics": metrics}
        if verdict:
            result["valuation"] = verdict
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(f"\nResults written to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
