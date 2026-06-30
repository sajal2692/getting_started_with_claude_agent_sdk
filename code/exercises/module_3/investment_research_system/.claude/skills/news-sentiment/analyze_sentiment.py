#!/usr/bin/env python3
"""
News Sentiment Analysis Helper Script

Analyzes the sentiment of financial news text and aggregates coverage into
key themes. This replaces the previous in-process sentiment custom tools with
a skill-driven helper script.
"""

import argparse
import json
import sys
from pathlib import Path

POSITIVE_KEYWORDS = [
    "beat", "exceeds", "strong", "growth", "profit", "surge",
    "bullish", "rally", "upgrade", "outperform", "buy",
    "innovation", "expansion", "record", "success",
]

NEGATIVE_KEYWORDS = [
    "miss", "below", "weak", "loss", "decline", "fall",
    "bearish", "concern", "downgrade", "underperform", "sell",
    "warning", "risk", "cut", "layoff", "lawsuit",
]

THEMES = {
    "Earnings & Financial Results": ["earnings", "revenue", "profit", "financial"],
    "Product & Innovation": ["product", "launch", "innovation", "technology"],
    "Market Performance": ["stock", "shares", "market", "trading"],
    "Management & Strategy": ["ceo", "executive", "strategy", "plan"],
    "Regulatory & Legal": ["lawsuit", "regulation", "sec", "investigation"],
}


def analyze_sentiment(text: str) -> dict:
    """Score sentiment from positive/negative keyword frequency."""
    lowered = text.lower()
    positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in lowered)
    negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in lowered)
    score = positive_count - negative_count

    if score > 2:
        classification = "Positive"
    elif score < -2:
        classification = "Negative"
    else:
        classification = "Neutral"

    return {
        "classification": classification,
        "score": score,
        "positive_signals": positive_count,
        "negative_signals": negative_count,
    }


def aggregate_themes(text: str):
    """Cluster news items (one per line) into common financial themes."""
    items = [line.strip() for line in text.split("\n") if line.strip()]
    theme_counts = {theme: 0 for theme in THEMES}
    for item in items:
        item_lower = item.lower()
        for theme, keywords in THEMES.items():
            if any(keyword in item_lower for keyword in keywords):
                theme_counts[theme] += 1
    return len(items), theme_counts


def build_report(sentiment: dict, total_items: int, theme_counts: dict) -> str:
    lines = ["News Sentiment Analysis", "=" * 50, ""]
    lines.append(f"Overall sentiment: {sentiment['classification']} (score {sentiment['score']:+d})")
    lines.append(
        f"Positive signals: {sentiment['positive_signals']} | "
        f"Negative signals: {sentiment['negative_signals']}"
    )
    lines.append("")
    lines.append(f"News items analyzed: {total_items}")
    lines.append("Key themes:")

    ranked = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    has_theme = False
    for theme, count in ranked:
        if count > 0:
            lines.append(f"  - {theme}: {count} item(s)")
            has_theme = True
    if not has_theme:
        lines.append("  - No dominant themes detected")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze sentiment and themes of financial news text"
    )
    parser.add_argument("--input", help="Path to a text file of news (one item per line)")
    parser.add_argument("--text", help="News text passed directly (alternative to --input)")
    parser.add_argument("--output", help="Optional path to write JSON results")
    args = parser.parse_args()

    if args.input:
        try:
            text = Path(args.input).read_text()
        except OSError as e:
            print(f"ERROR: could not read input file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("ERROR: provide --input <file> or --text <string>", file=sys.stderr)
        sys.exit(1)

    sentiment = analyze_sentiment(text)
    total_items, theme_counts = aggregate_themes(text)
    print(build_report(sentiment, total_items, theme_counts))

    if args.output:
        result = {
            "sentiment": sentiment,
            "total_items": total_items,
            "themes": {k: v for k, v in theme_counts.items() if v > 0},
        }
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(f"\nResults written to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
