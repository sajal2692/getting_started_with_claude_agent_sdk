"""
Competitive Analysis Tools

Custom tools for sector benchmarking and competitive positioning.
Used by the Competitive Analysis Subagent.
"""

from typing import Any, Dict
from claude_agent_sdk import tool
import json


@tool(
    "sector_benchmark",
    "Compares a stock's metrics against sector averages. Input should be JSON with stock metrics and sector averages.",
    {"benchmark_data": str}
)
async def sector_benchmark(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Benchmarks a stock against sector averages.

    Expected input format (JSON string):
    {
        "ticker": "AAPL",
        "stock": {
            "pe_ratio": 25.0,
            "profit_margin": 25.0,
            "roe": 150.0,
            "revenue_growth": 8.0
        },
        "sector_avg": {
            "pe_ratio": 22.0,
            "profit_margin": 15.0,
            "roe": 35.0,
            "revenue_growth": 10.0
        },
        "sector_name": "Technology"
    }
    """
    try:
        data = json.loads(args["benchmark_data"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format."
            }]
        }

    ticker = data.get("ticker", "Unknown")
    stock = data.get("stock", {})
    sector = data.get("sector_avg", {})
    sector_name = data.get("sector_name", "Unknown Sector")

    result = f"🏆 Sector Benchmark Analysis: {ticker}\n"
    result += f"Sector: {sector_name}\n"
    result += "=" * 50 + "\n\n"

    metrics = [
        ("P/E Ratio", "pe_ratio", False),
        ("Profit Margin (%)", "profit_margin", True),
        ("ROE (%)", "roe", True),
        ("Revenue Growth (%)", "revenue_growth", True)
    ]

    better_count = 0
    worse_count = 0

    for metric_name, key, higher_is_better in metrics:
        stock_value = stock.get(key, 0)
        sector_value = sector.get(key, 0)

        if stock_value == 0 or sector_value == 0:
            continue

        result += f"{metric_name}:\n"
        result += f"  {ticker}: {stock_value:.2f}\n"
        result += f"  Sector Avg: {sector_value:.2f}\n"

        # Determine if better or worse
        if higher_is_better:
            is_better = stock_value > sector_value
        else:
            # For P/E, lower can be better (but not always)
            is_better = stock_value < sector_value

        if is_better:
            diff_pct = abs((stock_value - sector_value) / sector_value * 100)
            result += f"  ✓ Outperforms sector by {diff_pct:.1f}%\n"
            better_count += 1
        else:
            diff_pct = abs((stock_value - sector_value) / sector_value * 100)
            result += f"  ⚠ Underperforms sector by {diff_pct:.1f}%\n"
            worse_count += 1

        result += "\n"

    # Overall positioning
    total_metrics = better_count + worse_count
    if total_metrics > 0:
        result += "Competitive Position: "
        if better_count > worse_count:
            result += "🥇 SECTOR LEADER\n"
            result += f"Outperforms on {better_count}/{total_metrics} metrics.\n"
        elif worse_count > better_count:
            result += "📊 SECTOR LAGGARD\n"
            result += f"Underperforms on {worse_count}/{total_metrics} metrics.\n"
        else:
            result += "➖ SECTOR AVERAGE\n"
            result += "Performance is in line with sector averages.\n"

    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }


@tool(
    "market_position_analyzer",
    "Analyzes a company's market position including market share, competitive advantages, and threats. Input should be JSON with position data.",
    {"position_data": str}
)
async def market_position_analyzer(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes competitive market position.

    Expected input format (JSON string):
    {
        "ticker": "AAPL",
        "market_share": 28.0,
        "rank": 1,
        "total_competitors": 5,
        "strengths": ["Brand loyalty", "Ecosystem", "Innovation"],
        "weaknesses": ["High prices", "Dependence on iPhone"],
        "market_trends": ["5G adoption", "AR/VR growth"]
    }
    """
    try:
        data = json.loads(args["position_data"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format."
            }]
        }

    ticker = data.get("ticker", "Unknown")
    market_share = data.get("market_share", 0)
    rank = data.get("rank", 0)
    total_competitors = data.get("total_competitors", 0)
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])
    trends = data.get("market_trends", [])

    result = f"🎯 Market Position Analysis: {ticker}\n"
    result += "=" * 50 + "\n\n"

    # Market Share
    result += f"Market Share: {market_share:.1f}%\n"
    if market_share > 25:
        result += "  → Market Leader\n"
    elif market_share > 15:
        result += "  → Strong Position\n"
    elif market_share > 5:
        result += "  → Moderate Position\n"
    else:
        result += "  → Niche Player\n"

    result += f"\nMarket Rank: #{rank} of {total_competitors} major competitors\n\n"

    # Competitive Strengths
    if strengths:
        result += "💪 Competitive Strengths:\n"
        for strength in strengths:
            result += f"  • {strength}\n"
        result += "\n"

    # Competitive Weaknesses
    if weaknesses:
        result += "⚠️  Competitive Weaknesses:\n"
        for weakness in weaknesses:
            result += f"  • {weakness}\n"
        result += "\n"

    # Market Trends
    if trends:
        result += "📈 Relevant Market Trends:\n"
        for trend in trends:
            result += f"  • {trend}\n"
        result += "\n"

    # Strategic Assessment
    result += "Strategic Assessment:\n"
    if market_share > 20 and len(strengths) > len(weaknesses):
        result += "  🟢 Strong competitive position with sustainable advantages.\n"
    elif market_share > 10:
        result += "  🟡 Solid position but facing competitive pressure.\n"
    else:
        result += "  🔴 Challenging position requiring strategic repositioning.\n"

    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }
