"""
Financial Analysis Tools

Custom tools for calculating financial metrics and ratios.
Used by the Fundamental Analysis Subagent.
"""

from typing import Any, Dict
from claude_agent_sdk import tool
import json


@tool(
    "financial_metrics_calculator",
    "Calculates key financial metrics (P/E ratio, ROE, profit margin, etc.) from stock data. Input should be JSON with price, earnings, revenue, equity.",
    {"stock_data": str}
)
async def financial_metrics_calculator(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates fundamental financial metrics from stock data.

    Expected input format (JSON string):
    {
        "ticker": "AAPL",
        "price": 150.0,
        "earnings_per_share": 6.0,
        "revenue": 365000000000,
        "net_income": 90000000000,
        "shareholders_equity": 60000000000,
        "shares_outstanding": 15000000000
    }
    """
    try:
        data = json.loads(args["stock_data"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format. Please provide valid stock data."
            }]
        }

    ticker = data.get("ticker", "Unknown")
    price = data.get("price", 0)
    eps = data.get("earnings_per_share", 0)
    revenue = data.get("revenue", 0)
    net_income = data.get("net_income", 0)
    equity = data.get("shareholders_equity", 0)
    shares = data.get("shares_outstanding", 1)

    result = f"📊 Financial Metrics for {ticker}\n"
    result += "=" * 50 + "\n\n"

    # P/E Ratio
    if eps > 0:
        pe_ratio = price / eps
        result += f"P/E Ratio: {pe_ratio:.2f}\n"
        if pe_ratio < 15:
            result += "  → Interpretation: Potentially undervalued\n"
        elif pe_ratio > 30:
            result += "  → Interpretation: Potentially overvalued or high growth expected\n"
        else:
            result += "  → Interpretation: Reasonably valued\n"
    else:
        result += "P/E Ratio: N/A (negative or zero earnings)\n"

    result += "\n"

    # Profit Margin
    if revenue > 0:
        profit_margin = (net_income / revenue) * 100
        result += f"Profit Margin: {profit_margin:.2f}%\n"
        if profit_margin > 20:
            result += "  → Interpretation: Excellent profitability\n"
        elif profit_margin > 10:
            result += "  → Interpretation: Good profitability\n"
        else:
            result += "  → Interpretation: Low profitability\n"
    else:
        result += "Profit Margin: N/A\n"

    result += "\n"

    # ROE (Return on Equity)
    if equity > 0:
        roe = (net_income / equity) * 100
        result += f"ROE (Return on Equity): {roe:.2f}%\n"
        if roe > 20:
            result += "  → Interpretation: Excellent returns for shareholders\n"
        elif roe > 15:
            result += "  → Interpretation: Good returns for shareholders\n"
        else:
            result += "  → Interpretation: Moderate returns for shareholders\n"
    else:
        result += "ROE: N/A\n"

    result += "\n"

    # Market Cap
    market_cap = price * shares
    result += f"Market Capitalization: ${market_cap:,.0f}\n"
    if market_cap > 200_000_000_000:
        result += "  → Category: Mega Cap\n"
    elif market_cap > 10_000_000_000:
        result += "  → Category: Large Cap\n"
    elif market_cap > 2_000_000_000:
        result += "  → Category: Mid Cap\n"
    else:
        result += "  → Category: Small Cap\n"

    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }


@tool(
    "valuation_assessor",
    "Assesses whether a stock is overvalued, fairly valued, or undervalued based on multiple metrics. Input should be JSON with P/E, PEG, P/B ratios.",
    {"valuation_data": str}
)
async def valuation_assessor(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides a holistic valuation assessment based on multiple ratios.

    Expected input format (JSON string):
    {
        "ticker": "AAPL",
        "pe_ratio": 25.0,
        "peg_ratio": 2.0,
        "pb_ratio": 8.0,
        "industry_avg_pe": 20.0
    }
    """
    try:
        data = json.loads(args["valuation_data"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format."
            }]
        }

    ticker = data.get("ticker", "Unknown")
    pe = data.get("pe_ratio", 0)
    peg = data.get("peg_ratio", 0)
    pb = data.get("pb_ratio", 0)
    industry_pe = data.get("industry_avg_pe", 20)

    result = f"💰 Valuation Assessment for {ticker}\n"
    result += "=" * 50 + "\n\n"

    signals = []

    # P/E Analysis
    if pe > 0:
        result += f"P/E Ratio: {pe:.2f} (Industry Avg: {industry_pe:.2f})\n"
        if pe < industry_pe * 0.8:
            signals.append("undervalued")
            result += "  ✓ Below industry average - potentially undervalued\n"
        elif pe > industry_pe * 1.2:
            signals.append("overvalued")
            result += "  ⚠ Above industry average - potentially overvalued\n"
        else:
            signals.append("fair")
            result += "  = In line with industry average\n"

    result += "\n"

    # PEG Ratio Analysis
    if peg > 0:
        result += f"PEG Ratio: {peg:.2f}\n"
        if peg < 1:
            signals.append("undervalued")
            result += "  ✓ Below 1.0 - undervalued relative to growth\n"
        elif peg > 2:
            signals.append("overvalued")
            result += "  ⚠ Above 2.0 - overvalued relative to growth\n"
        else:
            signals.append("fair")
            result += "  = Fairly valued relative to growth\n"

    result += "\n"

    # P/B Ratio Analysis
    if pb > 0:
        result += f"P/B Ratio: {pb:.2f}\n"
        if pb < 3:
            signals.append("undervalued")
            result += "  ✓ Below 3.0 - reasonable book value\n"
        elif pb > 10:
            signals.append("overvalued")
            result += "  ⚠ Above 10.0 - premium to book value\n"
        else:
            signals.append("fair")
            result += "  = Moderate premium to book value\n"

    result += "\n"

    # Overall Assessment
    overvalued_count = signals.count("overvalued")
    undervalued_count = signals.count("undervalued")

    result += "Overall Valuation: "
    if undervalued_count > overvalued_count:
        result += "📉 UNDERVALUED\n"
        result += f"Majority of signals ({undervalued_count}/{len(signals)}) suggest stock is trading below fair value.\n"
    elif overvalued_count > undervalued_count:
        result += "📈 OVERVALUED\n"
        result += f"Majority of signals ({overvalued_count}/{len(signals)}) suggest stock is trading above fair value.\n"
    else:
        result += "➖ FAIRLY VALUED\n"
        result += "Signals are mixed, suggesting the stock is trading near fair value.\n"

    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }
