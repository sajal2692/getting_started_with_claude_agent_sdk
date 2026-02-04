# Module 3: Multi-Agent Investment Research System

## Overview

This module demonstrates **advanced multi-agent architecture** using the Claude Agent SDK. Building on the stock analyzer from Module 2, this system showcases:

- **Custom Tools**: In-process MCP servers for domain-specific operations
- **Pre-built MCP**: Integration with Tavily Search for real-time news
- **Skills from Module 2**: Reuses stock-lookup, risk-analysis, comparative-analysis
- **New Skill**: Dashboard-design skill for visualization guidelines
- **Subagents**: Specialized agents with isolated contexts
- **Parallel Execution**: Multiple research agents running simultaneously
- **Sequential Orchestration**: Dashboard builder runs after research completes
- **Tool Restriction**: Different tools per subagent for security and specialization

### Key Improvements from Module 2

| Module 2 (Skills) | Module 3 (Multi-Agent) |
|-------------------|------------------------|
| Single agent with skills | Multiple specialized subagents |
| Sequential skill execution | Parallel research execution |
| Script-based analysis | Custom MCP tools + subagents |
| Text output | Interactive HTML dashboard |
| Single agent context | Isolated contexts per subagent |

## Architecture

```
Investment Research Coordinator (Main Agent)
         |
         | Spawns in PARALLEL:
         |
         +---> News & Sentiment Subagent
         |     • Tavily Search MCP (for real-time news)
         |     • sentiment_analyzer tool (custom)
         |     • news_aggregator tool (custom)
         |     → Returns: Sentiment summary
         |
         +---> Fundamental Analysis Subagent
         |     • stock-lookup skill (Module 2)
         |     • risk-analysis skill (Module 2)
         |     • financial_metrics_calculator tool (custom)
         |     • valuation_assessor tool (custom)
         |     → Returns: Financial analysis summary
         |
         +---> Competitive Analysis Subagent
               • comparative-analysis skill (Module 2)
               • sector_benchmark tool (custom)
               • market_position_analyzer tool (custom)
               → Returns: Competitive position summary
         |
         | Wait for all parallel research to complete
         |
         v
    Coordinator synthesizes findings
         |
         | Spawns SEQUENTIALLY:
         |
         +---> Dashboard Builder Subagent
               • dashboard-design skill (guidelines)
               • create_chart tool (EXCLUSIVE, custom)
               • build_dashboard tool (EXCLUSIVE, custom)
               → Creates: Interactive HTML dashboard
         |
         v
    Complete investment report with visualizations
```

## Project Structure

```
investment_research_system/
├── custom_tools/                           # Custom MCP tool implementations
│   ├── sentiment_tools.py                  # News sentiment analysis
│   ├── financial_tools.py                  # Financial metrics & valuation
│   ├── competitive_tools.py                # Sector benchmarking
│   └── visualization_tools.py              # Chart creation & dashboard
├── output/                                  # Generated dashboards
│   └── .gitkeep
├── tmp/                                     # Temporary data files
│   └── .gitkeep
├── investment_research.py                   # Main application
├── pyproject.toml                           # Dependencies
├── .env.example                             # API key template
├── .gitignore
└── README.md                                # This file
```

## What You'll Learn

### 1. **Custom Tools (In-Process MCP Servers)**

Create domain-specific tools packaged as MCP servers:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("sentiment_analyzer", "Analyzes sentiment", {"text": str})
async def sentiment_analyzer(args):
    # Tool implementation
    return {"content": [{"type": "text", "text": "Result"}]}

# Package as MCP server
server = create_sdk_mcp_server(
    name="sentiment-tools",
    tools=[sentiment_analyzer]
)
```

### 2. **Subagent Architecture**

Define specialized subagents with:
- Custom prompts and behavior
- Restricted tool access
- Isolated contexts
- Specific MCP servers

```python
subagents = {
    "news-sentiment": AgentDefinition(
        description="Analyzes news and sentiment",
        prompt="You are a financial news analyst...",
        tools=["Read", "mcp__sentiment-tools__sentiment_analyzer"],
        mcp_servers={"sentiment-tools": sentiment_server}
    )
}
```

### 3. **Parallel vs Sequential Execution**

- **Parallel**: Research subagents run simultaneously for speed
- **Sequential**: Dashboard builder waits for all research to complete

### 4. **Tool Restriction**

Security principle: Each subagent only gets tools it needs:
- News subagent: Cannot modify files or run bash commands
- Dashboard builder: ONLY has visualization tools
- Fundamental analyst: Has Module 2 skills + financial tools

### 5. **Context Isolation**

Each subagent has separate context:
- Prevents information overload in main agent
- Subagents return summaries, not raw data
- Main coordinator stays focused on synthesis

## Setup

### 1. Navigate to This Directory

```bash
cd code/exercises/module_3/investment_research_system
```

### 2. Install Dependencies

```bash
uv sync
```

This installs:
- claude-agent-sdk (≥0.1.19)
- yfinance (stock data)
- pandas, numpy (data analysis)
- python-dotenv (environment variables)

### 3. Configure API Key

**Option A**: Use parent project's .env (recommended)
```bash
# The script will look for .env in current directory,
# or fall back to ../../../../.env
```

**Option B**: Create local .env
```bash
cp .env.example .env
# Edit .env and add: CLAUDE_API_KEY=your_key_here
```

**Option C**: (Optional but Recommended) Tavily Search API for real news
```bash
# Get free key at: https://tavily.com/
# Free tier: 1000 searches/month
# Add to .env: TAVILY_API_KEY=your_key_here
# Without Tavily, news subagent uses only sentiment analysis tools
```

### 4. Verify Installation

```bash
uv run python investment_research.py --help
```

## Usage

### Query Mode (One-Shot Analysis)

For single analysis requests:

```bash
# Basic analysis
uv run python investment_research.py query "Analyze Tesla stock"

# Comprehensive research
uv run python investment_research.py query "Give me a full investment analysis of Apple"

# Specific questions
uv run python investment_research.py query "Should I invest in Microsoft? What are the risks?"

# Debug mode - see subagent activity
uv run python investment_research.py query --debug "Analyze NVIDIA"
```

### Interactive Mode (Conversation)

For multi-turn conversations:

```bash
# Standard mode
uv run python investment_research.py interactive

# Debug mode - see what's happening
uv run python investment_research.py interactive --debug
```

## Custom Tools Reference

### Sentiment Tools (News & Sentiment Subagent)

#### `sentiment_analyzer`
Analyzes sentiment of financial news text.

**Input**:
```json
{"text": "Amazon beats earnings expectations with strong cloud growth"}
```

**Output**: Sentiment score and classification (Positive/Negative/Neutral)

#### `news_aggregator`
Aggregates multiple news items and identifies themes.

**Input**: Newline-separated news items
**Output**: Theme categorization and summary

### Financial Tools (Fundamental Analysis Subagent)

#### `financial_metrics_calculator`
Calculates key financial metrics (P/E, ROE, profit margin, etc.).

**Input**:
```json
{
  "ticker": "AAPL",
  "price": 150.0,
  "earnings_per_share": 6.0,
  "revenue": 365000000000,
  "net_income": 90000000000,
  "shareholders_equity": 60000000000,
  "shares_outstanding": 15000000000
}
```

**Output**: Formatted metrics with interpretations

#### `valuation_assessor`
Provides holistic valuation assessment.

**Input**:
```json
{
  "ticker": "AAPL",
  "pe_ratio": 25.0,
  "peg_ratio": 2.0,
  "pb_ratio": 8.0,
  "industry_avg_pe": 20.0
}
```

**Output**: Valuation assessment (Overvalued/Fair/Undervalued)

### Competitive Tools (Competitive Analysis Subagent)

#### `sector_benchmark`
Compares stock metrics against sector averages.

**Input**: Stock and sector metrics (JSON)
**Output**: Competitive position analysis

#### `market_position_analyzer`
Analyzes market position, strengths, weaknesses.

**Input**: Market share, competitive data (JSON)
**Output**: Strategic position assessment

### Visualization Tools (Dashboard Builder Only)

#### `create_chart`
Creates HTML/JavaScript charts using Chart.js.

**Input**:
```json
{
  "chart_type": "bar",
  "title": "Returns Comparison",
  "labels": ["AAPL", "MSFT", "GOOGL"],
  "datasets": [{
    "label": "Returns (%)",
    "data": [15.2, 12.8, 18.5]
  }]
}
```

**Output**: HTML chart snippet

#### `build_dashboard`
Assembles complete HTML dashboard.

**Input**: Dashboard configuration with sections and charts (JSON)
**Output**: Complete HTML file in `output/` directory

## How It Works

### 1. Coordinator Receives Request

Main agent receives investment research request:
```
"Analyze Tesla stock"
```

### 2. Parallel Research Phase

Coordinator spawns 3 subagents **simultaneously**:

```python
# Pseudo-code of what happens internally
parallel:
    news_sentiment_result = spawn_subagent("news-sentiment")
    fundamental_result = spawn_subagent("fundamental-analysis")
    competitive_result = spawn_subagent("competitive-analysis")

wait_for_all_to_complete()
```

Each subagent:
- Has isolated context
- Uses only its assigned tools
- Returns concise summary (not raw data)
- Runs independently

### 3. Synthesis

Coordinator receives all summaries and synthesizes:
- Overall sentiment
- Valuation assessment
- Competitive positioning
- Investment recommendation

### 4. Sequential Dashboard Building

After synthesis, coordinator spawns dashboard builder **sequentially**:

```python
dashboard_result = spawn_subagent(
    "dashboard-builder",
    context=all_research_summaries + synthesis
)
```

Dashboard builder:
- Creates charts from metrics
- Assembles HTML dashboard
- Saves to `output/` directory
- Returns link to user

## Key Concepts

### Parallel Execution

```python
# Research subagents run in parallel
# This means 3x speed improvement!
Subagent A: ████████░░░░ (0.5s to complete)
Subagent B: ████████████ (0.6s to complete)
Subagent C: ████████░░░░ (0.5s to complete)
Total time: ~0.6s (instead of 1.6s sequential)
```

### Context Isolation

**Without isolation** (Single agent):
```
Main Agent Context:
- 100 news articles
- 50 financial metrics
- 30 competitor analyses
→ Context overload! Poor results.
```

**With isolation** (Subagents):
```
Main Agent Context:
- News summary (5 bullet points)
- Financial summary (5 bullet points)
- Competitive summary (5 bullet points)
→ Focused context! Great synthesis.
```

### Tool Restriction

Security and specialization through tool isolation:

| Subagent | Read | Write | Bash | Custom Tools | MCP |
|----------|------|-------|------|--------------|-----|
| News & Sentiment | Yes | Yes | No | sentiment_analyzer | - |
| Fundamental | Yes | Yes | Yes | financial_metrics_calculator | - |
| Competitive | Yes | Yes | Yes | sector_benchmark | - |
| Dashboard | Yes | Yes | No | create_chart, build_dashboard | - |

**Why?**
- News subagent doesn't need bash access
- Dashboard builder doesn't need analysis tools
- Principle of least privilege

## Generated Output

### HTML Dashboard

Located in `output/investment_report_{ticker}_{date}.html`

**Features**:
- Executive summary cards (sentiment, valuation, recommendation)
- Interactive Chart.js visualizations
- News & sentiment analysis section
- Financial metrics with charts
- Competitive benchmarking
- Responsive design
- Professional styling

**Open in browser**:
```bash
open output/investment_report_AAPL_2025-02-04.html
# Or just double-click the file
```

## Module 2 Skills Integration

This system **builds on Module 2** by reusing and extending its skills:

**Skills included** (in `.claude/skills/`):
- `stock-lookup`: Fetch historical stock data (from Module 2)
- `risk-analysis`: Calculate risk metrics (from Module 2)
- `comparative-analysis`: Compare multiple stocks (from Module 2)
- `dashboard-design`: Dashboard design guidelines (**new in Module 3**)

**Which subagents use which skills**:
- **Fundamental Analysis**: Uses `stock-lookup`, `risk-analysis` + custom financial tools
- **Competitive Analysis**: Uses `comparative-analysis` + custom competitive tools
- **Dashboard Builder**: Uses `dashboard-design` + custom visualization tools
- **News & Sentiment**: Only Tavily MCP + custom sentiment tools (no skills needed)

**Key takeaway**: This demonstrates that:
- Skills are portable and reusable across modules
- Subagents can combine skills with custom tools
- Different subagents get different tool/skill combinations

## Troubleshooting

### Subagents Not Spawning

**Problem**: Main agent doesn't spawn subagents

**Solution**:
```python
# Check: Task tool included?
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Task"],  # ← Required!
)
```

### Custom Tools Not Working

**Problem**: "Tool not found" errors

**Solution**:
```python
# Verify MCP servers registered
options = ClaudeAgentOptions(
    mcp_servers={"sentiment-tools": sentiment_server},
    allowed_tools=["mcp__sentiment-tools__sentiment_analyzer"]
)
```

### Dashboard Not Generated

**Problem**: No dashboard file created

**Solution**:
```bash
# Ensure output directory exists
mkdir -p output

# Check permissions
ls -ld output/

# Verify dashboard builder has visualization tools
# Check investment_research.py AgentDefinition for "dashboard-builder"
```

### Performance Issues

**Problem**: System is slow

**Causes & Solutions**:
1. **Subagents running sequentially**: Verify parallel spawning in prompts
2. **Too much data**: Ensure subagents return summaries, not raw data
3. **Context overload**: Check that isolation is working properly

## Cost Optimization

### Typical Costs (Sonnet 4.5)

| Operation | Approximate Cost |
|-----------|------------------|
| Single stock analysis (all 3 research subagents) | $0.15-0.30 |
| Dashboard generation | $0.05-0.10 |
| Interactive session (3-4 turns) | $0.40-0.80 |

### Tips for Reducing Costs

1. **Use Haiku for research subagents**:
```python
subagents = {
    "news-sentiment": AgentDefinition(
        ...
        model="haiku"  # Cheaper for simple tasks
    )
}
```

2. **Enable prompt caching**:
- Already enabled by default in SDK
- 2nd, 3rd queries in session ~50% cheaper

3. **Limit subagent output**:
- Ensure subagents return summaries (5-7 bullet points)
- Avoid raw data dumps

4. **Use query mode for one-off analyses**:
- Interactive mode keeps context across turns
- Query mode starts fresh (no context accumulation)

## Learning Exercises

### Exercise 1: Add a Risk Analysis Subagent

Create a 4th parallel subagent for risk assessment:
- VaR calculations
- Beta analysis
- Maximum drawdown
- Risk categorization

**Challenge**: Ensure it runs in parallel with others

### Exercise 2: Implement Brave Search MCP

Integrate real Brave Search:
1. Get API key from https://brave.com/search/api/
2. Configure Brave Search MCP in news subagent
3. Search for real-time news

### Exercise 3: Custom Chart Types

Extend visualization tools:
- Add radar charts for multi-metric comparison
- Add gauge charts for risk levels
- Create time-series line charts

### Exercise 4: Sequential Analysis Pipeline

Modify architecture to run sequentially with data flow:
```
News → Fundamental (uses news sentiment) → Competitive (uses both) → Dashboard
```

**Challenge**: Pass data between subagents

### Exercise 5: Portfolio Analysis

Extend to analyze multiple stocks:
- Accept portfolio of tickers
- Run research for each in parallel
- Create comparative dashboard

## Best Practices

### 1. Design for Parallelism

```python
# Good - Independent subagents
news_agent: Search news (no dependencies)
financial_agent: Analyze metrics (no dependencies)
competitive_agent: Benchmark (no dependencies)
→ Can run in parallel!

# Bad - Sequential dependencies
agent_1: Fetch data
agent_2: Process agent_1 results (must wait)
agent_3: Process agent_2 results (must wait)
→ No parallelism benefit
```

### 2. Return Summaries, Not Raw Data

```python
# Good - Concise summary
return """
Key findings:
• Sentiment: Positive (score +5)
• Main themes: Product launch, earnings beat
• Overall market perception: Bullish
"""

# Bad - Raw data dump
return """
[100 news articles in full text...]
"""
```

### 3. Restrict Tools by Need

```python
# Good - Minimal tools
"news-sentiment": {
    "tools": ["Read", "mcp__sentiment__analyzer"]  # Only what's needed
}

# Bad - Too permissive
"news-sentiment": {
    "tools": ["*"]  # Has access to everything!
}
```

### 4. Clear Subagent Descriptions

```python
# Good - Specific trigger keywords
description="Analyzes news and sentiment for stocks. Use when you need current events, news analysis, or sentiment."

# Bad - Vague
description="Helps with analysis"
```

### 5. Test Isolation

Verify subagents don't see each other's contexts:
```python
# Each subagent should only see:
# - Its own prompt
# - The coordinator's query
# - NOT other subagents' results (until coordinator synthesizes)
```

## Key Takeaways

1. **Multi-agent > Single agent**: Parallel execution, specialized expertise, context isolation
2. **Custom tools**: In-process MCP servers for domain logic
3. **Tool restriction**: Security through least privilege
4. **Context management**: Subagents return summaries, not raw data
5. **Orchestration patterns**: Parallel for speed, sequential for dependencies
6. **Visual output**: Dashboards make insights actionable

## Next Steps

After completing Module 3:
- **Advanced patterns**: Agent hierarchies, recursive subagents (within limits)
- **Production deployment**: Error handling, monitoring, cost controls
- **Real-world integration**: Connect to live APIs, databases, internal systems
- **Custom MCP servers**: Build standalone MCP servers for reuse

## Resources

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/python)
- [Subagents Guide](https://platform.claude.com/docs/en/agent-sdk/subagents)
- [Custom Tools Documentation](https://platform.claude.com/docs/en/agent-sdk/custom-tools)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Happy researching!**
