# Module 3: Multi-Agent Investment Research System

A multi-agent CLI application that uses subagents for parallel research and generates interactive HTML dashboards. Demonstrates custom MCP tools, agent coordination, and visualization.

## Architecture

The coordinator agent spawns specialized subagents:

**Parallel Research Phase:**
- News & Sentiment Subagent (custom sentiment tools + Tavily Search MCP)
- Fundamental Analysis Subagent (stock-lookup, risk-analysis, financial tools)
- Competitive Analysis Subagent (comparative-analysis, sector tools)

**Sequential Building Phase:**
- Dashboard Builder Subagent (creates interactive HTML with Chart.js)

## Project Structure

```
investment_research_system/
├── custom_tools/                # Custom MCP tools
│   ├── sentiment_tools.py       # News sentiment analysis
│   ├── financial_tools.py       # Financial metrics & valuation
│   ├── competitive_tools.py     # Sector benchmarking
│   └── visualization_tools.py   # Chart creation & dashboard
├── .claude/skills/              # Reused from Module 2
│   ├── stock-lookup/
│   ├── risk-analysis/
│   ├── comparative-analysis/
│   └── dashboard-design/        # New: visualization guidelines
├── output/                      # Generated HTML dashboards
├── tmp/                         # Temporary data files
├── investment_research.py       # Main application
├── pyproject.toml
├── .env.example
└── README.md
```

## Setup

1. Navigate to this directory:
```bash
cd code/exercises/module_3/investment_research_system
```

2. Install dependencies:
```bash
uv sync
```

3. Configure API keys (choose one):
```bash
# Option A: Use parent project's .env (recommended)
# The script will look for ../../../../.env

# Option B: Create local .env
cp .env.example .env
# Edit .env and add:
#   CLAUDE_API_KEY=your_key_here
#   TAVILY_API_KEY=your_key_here (optional, for real news search)
```

Note: Tavily API is optional (free tier: 1000 searches/month at https://tavily.com/). Without it, the news subagent uses only sentiment analysis tools.

## Running the Application

### Query Mode:
```bash
uv run python investment_research.py query "Analyze Tesla stock"
uv run python investment_research.py query --debug "Full investment analysis of Apple"
```

### Interactive Mode:
```bash
uv run python investment_research.py interactive
uv run python investment_research.py interactive --debug
```

## Expected Output

The system generates:

1. **Comprehensive research** by coordinating specialized subagents:
   - News & sentiment analysis
   - Fundamental financial metrics
   - Competitive positioning

2. **Interactive HTML dashboard** in `output/investment_report_{ticker}_{date}.html`:
   - Executive summary cards
   - Chart.js visualizations
   - News sentiment section
   - Financial metrics charts
   - Competitive benchmarking

3. **Temporary data files** in `tmp/`:
   - Stock data, risk metrics, comparisons

Example workflow:
```
You: Analyze Tesla stock

System spawns 3 subagents in parallel:
├─ News & Sentiment (Tavily search + sentiment tools)
├─ Fundamental Analysis (stock-lookup, risk-analysis, financial tools)
└─ Competitive Analysis (comparative-analysis, sector tools)

Coordinator synthesizes findings

Dashboard Builder creates HTML report
→ output/investment_report_TSLA_2025-02-05.html

Open in browser to view interactive dashboard
```

The `--debug` flag shows subagent activity and tool usage in detail.
