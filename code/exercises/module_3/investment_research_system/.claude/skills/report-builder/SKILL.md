---
name: report-builder
description: Assemble a complete interactive HTML dashboard (Chart.js) from a JSON config. Use AFTER research is complete to render summary cards, sections, and charts into a single shareable report file.
---

# Report Builder Skill

## Purpose
This skill assembles a polished, self-contained HTML dashboard from a JSON
config. It renders summary cards, content sections, and Chart.js charts into one
file you can open in a browser. Pair it with the `dashboard-design` skill, which
provides the visual guidelines (colors, chart types, layout) this report follows.

## When to Use
Use this skill when:
- All research is complete and you need to visualize the findings
- You want an interactive HTML report with charts and summary cards
- You are the dashboard-builder step of the investment research workflow

## Why a Helper Script (Not Inline HTML)
You pass a compact JSON config and the script generates the full HTML. Keeping the
large HTML/CSS out of the model's output keeps responses small and avoids
truncated dashboards on big reports. Charts are described as small specs and
rendered to Chart.js by the script.

## Workflow

### 1. Consult `dashboard-design`
Review the `dashboard-design` skill for the color scheme, chart-type choices, and
layout structure before building the config.

### 2. Build the Config
Write a JSON config to `tmp/`. Sections may include a `chart_spec` (rendered to
Chart.js by the script) or pre-rendered `chart` HTML.

Example `tmp/dashboard_config.json`:
```json
{
  "title": "Investment Research Report",
  "company": "Apple Inc. (AAPL)",
  "date": "2026-06-30",
  "summary": {
    "sentiment": "Positive",
    "valuation": "Fairly Valued",
    "recommendation": "Buy"
  },
  "sections": [
    {
      "title": "Financial Metrics",
      "content": "<p>P/E 30.5, ROE 156%, margin 25%.</p>",
      "chart_spec": {
        "chart_type": "bar",
        "title": "Key Metrics",
        "labels": ["P/E", "Profit Margin %", "ROE %"],
        "datasets": [{
          "label": "AAPL",
          "data": [30.5, 25.3, 156.4],
          "backgroundColor": ["#667eea", "#4CAF50", "#4CAF50"]
        }]
      }
    },
    {
      "title": "News & Sentiment",
      "content": "<p>Coverage skews bullish on services growth.</p>"
    }
  ]
}
```

### 3. Run the Helper Script
```bash
uv run python .claude/skills/report-builder/build_report.py \
  --input tmp/dashboard_config.json \
  --output outputs/session_<ts>/final/investment_report_AAPL_2026-06-30.html
```

**Arguments**:
- `--input` (required): Path to the JSON dashboard config
- `--output` (required): Path to write the HTML file

### 4. Confirm the Output
The script prints the output path and a `file://` link. Report that path back so
the user can open the dashboard.

## Config Reference
- `title`, `company`, `date`: header text
- `summary`: object of label -> value; values containing "positive"/"buy" render
  green, "negative"/"sell" render red, otherwise orange
- `sections`: list of `{ title, content (HTML), chart_spec | chart_specs | chart }`
- `chart_spec`: a single `{ chart_type, title, labels, datasets }` (Chart.js)
- `chart_specs`: a list of chart specs, to render several charts in one section

## Important Notes
- Build summary cards for sentiment, valuation, and recommendation at minimum
- Follow `dashboard-design` colors: green positive, red negative, orange neutral
- Keep `content` concise HTML; let charts carry the comparisons
- Use absolute paths for `--input` and `--output`
- Use `uv run python` to execute (not plain `python`)
