"""
Sentiment Analysis Tools

Custom tools for analyzing news sentiment and aggregating financial news.
Used by the News & Sentiment Subagent.
"""

from typing import Any, Dict
from claude_agent_sdk import tool


@tool(
    "sentiment_analyzer",
    "Analyzes sentiment of financial news text. Returns sentiment score and classification (Positive/Negative/Neutral).",
    {"text": str}
)
async def sentiment_analyzer(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple rule-based sentiment analysis for financial news.

    Returns sentiment score and classification based on keyword matching.
    """
    text = args["text"].lower()

    # Financial sentiment keywords
    positive_keywords = [
        "beat", "exceeds", "strong", "growth", "profit", "surge",
        "bullish", "rally", "upgrade", "outperform", "buy",
        "innovation", "expansion", "record", "success"
    ]

    negative_keywords = [
        "miss", "below", "weak", "loss", "decline", "fall",
        "bearish", "concern", "downgrade", "underperform", "sell",
        "warning", "risk", "cut", "layoff", "lawsuit"
    ]

    # Count keyword occurrences
    positive_count = sum(1 for word in positive_keywords if word in text)
    negative_count = sum(1 for word in negative_keywords if word in text)

    # Calculate score
    score = positive_count - negative_count

    # Classify sentiment
    if score > 2:
        classification = "Positive"
        emoji = "📈"
    elif score < -2:
        classification = "Negative"
        emoji = "📉"
    else:
        classification = "Neutral"
        emoji = "➖"

    result = f"{emoji} Sentiment: {classification} (Score: {score:+d})\n"
    result += f"Positive signals: {positive_count} | Negative signals: {negative_count}"

    return {
        "content": [
            {
                "type": "text",
                "text": result
            }
        ]
    }


@tool(
    "news_aggregator",
    "Aggregates and summarizes multiple news items into a structured format with key themes.",
    {"news_items": str}
)
async def news_aggregator(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates news items and identifies key themes.

    Takes a string of news items (separated by newlines or delimiters)
    and provides a structured summary.
    """
    news_text = args["news_items"]

    # Split into individual items (assuming line-separated)
    items = [item.strip() for item in news_text.split("\n") if item.strip()]

    result = f"📰 News Aggregation Summary\n"
    result += f"Total items analyzed: {len(items)}\n\n"

    # Identify common themes (simple keyword clustering)
    themes = {
        "Earnings & Financial Results": ["earnings", "revenue", "profit", "financial"],
        "Product & Innovation": ["product", "launch", "innovation", "technology"],
        "Market Performance": ["stock", "shares", "market", "trading"],
        "Management & Strategy": ["ceo", "executive", "strategy", "plan"],
        "Regulatory & Legal": ["lawsuit", "regulation", "sec", "investigation"]
    }

    theme_counts = {theme: 0 for theme in themes}

    for item in items:
        item_lower = item.lower()
        for theme, keywords in themes.items():
            if any(keyword in item_lower for keyword in keywords):
                theme_counts[theme] += 1

    result += "Key Themes:\n"
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            result += f"  • {theme}: {count} items\n"

    return {
        "content": [
            {
                "type": "text",
                "text": result
            }
        ]
    }
