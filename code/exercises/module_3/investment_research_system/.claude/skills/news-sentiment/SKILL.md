---
name: news-sentiment
description: Analyze the sentiment of financial news and aggregate coverage into key themes. Use when you need to assess market sentiment, gauge media coverage, or decide whether news about a stock is bullish, bearish, or neutral.
---

# News Sentiment Skill

## Purpose
This skill scores the sentiment of financial news text and groups coverage into
common themes (earnings, products, market performance, management, regulation).
It helps turn a batch of raw headlines or articles into a quick read on market mood.

## When to Use
Use this skill when the user (or a coordinating agent):
- Wants to know the overall sentiment of recent news ("bullish or bearish?")
- Needs to summarize a set of headlines or articles
- Asks about media coverage, themes, or market perception of a stock

## Capabilities
- Classify sentiment as Positive / Negative / Neutral with a numeric score
- Count positive vs. negative signals
- Cluster news items into key themes
- Optionally export results to JSON

## Workflow

### 1. Gather News Text
Collect the news you want to analyze. If you used the Tavily Search MCP, save the
returned headlines/snippets to a file (one item per line) in `tmp/`.

### 2. Run the Helper Script
The helper script `analyze_sentiment.py` does the scoring and theme aggregation:

```bash
uv run python .claude/skills/news-sentiment/analyze_sentiment.py \
  --input tmp/news.txt \
  --output tmp/sentiment.json
```

You can also pass text directly instead of a file:

```bash
uv run python .claude/skills/news-sentiment/analyze_sentiment.py \
  --text "Company beats earnings; analysts upgrade to buy"
```

**Arguments**:
- `--input` (optional): Path to a text file of news, one item per line
- `--text` (optional): News text passed directly (use instead of `--input`)
- `--output` (optional): Path to write JSON results (e.g., `tmp/sentiment.json`)

Provide either `--input` or `--text`.

### 3. Interpret the Results
- **Positive** (score > 2): coverage skews bullish
- **Negative** (score < -2): coverage skews bearish
- **Neutral** (otherwise): mixed or balanced coverage

Use the theme counts to highlight what the news is actually about (e.g., mostly
earnings vs. mostly regulatory concerns).

## Output Format

When `--output` is supplied, the script writes JSON like:
```json
{
  "sentiment": {
    "classification": "Positive",
    "score": 4,
    "positive_signals": 5,
    "negative_signals": 1
  },
  "total_items": 8,
  "themes": {
    "Earnings & Financial Results": 4,
    "Product & Innovation": 2
  }
}
```

## Important Notes
- Sentiment is a fast, rule-based keyword heuristic, not a market signal on its own
- Combine it with the actual headlines for context before drawing conclusions
- Use absolute paths under `tmp/` for input/output files
- Use `uv run python` to execute (not plain `python`)
