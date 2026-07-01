# Module 3: Multi-Agent Investment Research System

A multi-agent CLI application that uses subagents for parallel research and generates interactive HTML dashboards. Demonstrates Agent Skills with helper scripts, a pre-built MCP server (Tavily), agent coordination, and context isolation.

## Architecture

The coordinator agent spawns specialized subagents, each scoped to only the skills it needs:

**Parallel Research Phase:**
- News & Sentiment Subagent (`news-sentiment` skill + Tavily Search MCP)
- Fundamental Analysis Subagent (`stock-lookup`, `risk-analysis`, `financial-analysis` skills)
- Competitive Analysis Subagent (`comparative-analysis`, `competitive-positioning` skills)

**Sequential Building Phase:**
- Dashboard Builder Subagent (`dashboard-design` + `report-builder` skills; interactive Chart.js HTML)

All domain logic lives in Agent Skills with helper scripts. The only MCP server is the external, pre-built Tavily Search (a connectivity example); there are no in-process custom tools.

## Project Structure

```
investment_research_system/
├── .claude/skills/                  # All domain logic lives in skills
│   ├── stock-lookup/                # Fetch price history (helper script)
│   ├── risk-analysis/               # Volatility, beta, VaR (helper script)
│   ├── comparative-analysis/        # Compare tickers (helper script)
│   ├── news-sentiment/              # Sentiment + theme aggregation (helper script)
│   ├── financial-analysis/          # Metrics + valuation (helper script)
│   ├── competitive-positioning/     # Sector benchmark + position (helper script)
│   ├── dashboard-design/            # Dashboard design guidelines
│   └── report-builder/              # Assemble HTML dashboard (helper script)
├── outputs/                         # Generated dashboards + temp files (per session)
├── tmp/                             # Temporary data files
├── investment_research.py           # Main application
├── logger.py                        # Debug/observability logging
├── pyproject.toml
├── .env.example
└── README.md
```

The first three skills are carried forward from Module 2; the other four replace what used to be in-process custom tools.

## Setup

1. Navigate to this directory:
```bash
cd code/exercises/module_3/investment_research_system
```

2. Install dependencies:
```bash
uv sync
```

3. Authenticate:
```bash
# Default: use your Claude subscription -- no API key needed.
# Install the Claude Code CLI and log in once:
#   curl -fsSL https://claude.ai/install.sh | bash   # then: claude
#
# Optional (API-key billing instead): create a local .env and add your key
#   cp .env.example .env
#   # then uncomment ANTHROPIC_API_KEY in .env and paste your key
# (If ANTHROPIC_API_KEY is set, it overrides your subscription.)
```

Note: Tavily API is optional (free tier: 1000 searches/month at https://tavily.com/). To enable real-time news search, uncomment `TAVILY_API_KEY` in `.env` and add your key. Without it, the news subagent relies on the `news-sentiment` skill only.

Note: Output token limit (optional). Only relevant with per-token API billing (`ANTHROPIC_API_KEY`). If a large dashboard comes out truncated, raise the agent's output cap by setting `CLAUDE_CODE_MAX_OUTPUT_TOKENS` (e.g. `64000`) in `.env`. The default is fine for the subscription path and most reports; the `report-builder` skill also keeps the HTML out of the model's output, so this is rarely needed.

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

2. **Interactive HTML dashboard** in `outputs/session_<ts>/final/investment_report_{ticker}_{date}.html`:
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
├─ News & Sentiment (Tavily search + news-sentiment skill)
├─ Fundamental Analysis (stock-lookup, risk-analysis, financial-analysis skills)
└─ Competitive Analysis (comparative-analysis, competitive-positioning skills)

Coordinator synthesizes findings

Dashboard Builder creates HTML report
→ outputs/session_<ts>/final/investment_report_TSLA_2025-02-05.html

Open in browser to view interactive dashboard
```

The `--debug` flag shows subagent activity and tool usage in detail.
