# Module 2: Stock Analyzer with Agent Skills

A standalone CLI application demonstrating reusable agent skills. Instead of writing new scripts each time, the agent uses pre-built skills for stock analysis.

## Project Structure

```
stock_analyzer_with_skills/
├── .claude/skills/                  # Agent skills
│   ├── stock-lookup/                # Fetch stock data
│   ├── comparative-analysis/        # Compare stocks
│   └── risk-analysis/               # Risk assessment
├── tmp/                             # Generated analysis files
├── stock_analyzer.py                # Main CLI application
├── pyproject.toml
├── .env.example
└── README.md
```

## Setup

1. Navigate to this directory:
```bash
cd code/exercises/module_2/stock_analyzer_with_skills
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

## Running the Application

### Query Mode (one-off questions):
```bash
uv run python stock_analyzer.py query "Analyze Apple stock performance"
uv run python stock_analyzer.py query "Compare Tesla and Ford stocks"
uv run python stock_analyzer.py query --debug "How risky is Netflix?"
```

### Interactive Mode (conversations):
```bash
uv run python stock_analyzer.py interactive
uv run python stock_analyzer.py interactive --debug
```

## Available Skills

The agent can automatically use these skills based on your questions:

- **stock-lookup**: Fetch historical stock data ("analyze AAPL", "look up Tesla")
- **comparative-analysis**: Compare multiple stocks ("compare AAPL and MSFT")
- **risk-analysis**: Risk assessment ("how risky is Tesla?", "calculate beta")

## Expected Output

Analysis files are saved to `tmp/`:
- `tmp/aapl_data.json` - Stock data
- `tmp/comparison.json` - Comparative analysis results
- `tmp/risk_analysis.json` - Risk metrics

Example interaction:
```
You: Look up Tesla stock for the last 6 months
Agent: [Uses stock-lookup skill, analyzes TSLA data]

You: How does that compare to Ford?
Agent: [Uses comparative-analysis skill, compares both]

You: What's the risk level?
Agent: [Uses risk-analysis skill, provides risk metrics]
```

The `--debug` flag shows detailed tool execution and results.
