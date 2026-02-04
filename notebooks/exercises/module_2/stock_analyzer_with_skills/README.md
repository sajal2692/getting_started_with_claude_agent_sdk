# Module 2: Stock Analyzer with Agent Skills

## Overview

This module demonstrates the power of **Agent Skills** in the Claude Agent SDK. Unlike Module 1 where the agent wrote new scripts for every analysis, this module provides **reusable skills** that the agent can invoke on-demand.

### Key Improvements from Module 1

| Module 1 (Notebooks) | Module 2 (Skills) |
|---------------------|-------------------|
| Agent writes scripts every time | Agent uses pre-built skills |
| Repetitive code generation | Reusable capabilities |
| Jupyter notebook environment | Standalone Python application |
| Package management complexity | Clean uv environment |
| Single-shot or pre-scripted | True interactive mode |

### What You'll Learn

1. **Agent Skills**: Creating and using filesystem-based skills
2. **Progressive Disclosure**: How Claude discovers and uses skills
3. **Dual-Mode Operation**: Building query + interactive modes
4. **Clean Architecture**: Proper project structure for agent applications
5. **Real-World Patterns**: Production-ready agent design

## Project Structure

```
stock_analyzer_with_skills/
├── .claude/
│   └── skills/                      # Agent skills directory
│       ├── stock-lookup/            # Skill: Fetch stock data
│       │   ├── SKILL.md             # Skill definition
│       │   └── fetch_stock.py       # Helper script
│       ├── comparative-analysis/    # Skill: Compare stocks
│       │   ├── SKILL.md
│       │   └── compare_stocks.py
│       └── risk-analysis/           # Skill: Risk assessment
│           ├── SKILL.md
│           └── analyze_risk.py
├── tmp/                             # Generated files
│   └── .gitkeep
├── stock_analyzer.py                # Main CLI application
├── pyproject.toml                   # Dependencies
├── .env.example                     # API key template
├── .gitignore
└── README.md                        # This file
```

## Setup

### 1. Navigate to This Directory

```bash
cd notebooks/exercises/module_2/stock_analyzer_with_skills
```

### 2. Install Dependencies

```bash
uv sync
```

This installs:
- claude-agent-sdk (≥0.1.19)
- yfinance (stock data)
- pandas, numpy, scipy (data analysis)
- python-dotenv (environment variables)

### 3. Configure API Key

**Option A**: Use parent project's .env (recommended)
```bash
# The script will look for .env in current directory,
# or fall back to ../../../.env
```

**Option B**: Create local .env
```bash
cp .env.example .env
# Edit .env and add: CLAUDE_API_KEY=your_key_here
```

### 4. Verify Installation

```bash
uv run python stock_analyzer.py --help
```

## Usage

The stock analyzer has two modes: **query** (one-off) and **interactive** (chat).

### Query Mode

For one-off questions:

```bash
# Basic stock analysis
uv run python stock_analyzer.py query "Analyze Apple stock performance over the last year"

# Comparative analysis
uv run python stock_analyzer.py query "Compare Tesla, Ford, and GM stocks"

# Risk analysis
uv run python stock_analyzer.py query "How risky is Netflix stock?"

# Complex queries
uv run python stock_analyzer.py query "Compare AAPL and MSFT, then analyze which has lower risk"

# Debug mode - see what's happening under the hood
uv run python stock_analyzer.py query --debug "Analyze Google stock"
```

### Interactive Mode

For conversations with context:

```bash
# Standard mode
uv run python stock_analyzer.py interactive

# Debug mode - see tool commands and results
uv run python stock_analyzer.py interactive --debug
```

### Debug Mode

Both query and interactive modes support `--debug` flag to show:
- Exact bash commands executed
- Tool results and script outputs
- File paths being read
- JSON data content
- Full command arguments (not truncated)

**When to use debug mode**:
- Troubleshooting issues
- Understanding how skills work
- Verifying data accuracy
- Learning the agent's workflow
- Checking file locations

**Example session**:
```
You: Look up Tesla stock for the last 6 months
[Agent uses stock-lookup skill]
Assistant: Tesla (TSLA) has shown...

You: How does that compare to Ford?
[Agent uses comparative-analysis skill]
Assistant: Comparing TSLA and F over the same period...

You: What's the risk level of Tesla?
[Agent uses risk-analysis skill]
Assistant: Tesla has HIGH risk with 42% volatility...

You: quit
Session ended. Goodbye!
```

## Available Skills

### 1. stock-lookup

**Purpose**: Fetch historical stock data for any ticker

**When to use**: "analyze AAPL", "look up Tesla", "get data for Microsoft"

**Capabilities**:
- Historical price data (any period: 1mo to max)
- Current prices and statistics
- Volume information
- Export to JSON/CSV

**Example**:
```
You: Look up Netflix stock for the last year
Agent: [Uses stock-lookup skill]
       Fetches NFLX data, provides analysis
```

### 2. comparative-analysis

**Purpose**: Compare multiple stocks side-by-side

**When to use**: "compare AAPL and MSFT", "which performed better", "contrast Tesla and Rivian"

**Capabilities**:
- Side-by-side performance metrics
- Returns and volatility comparison
- Correlation analysis
- Rankings (best/worst performer)

**Example**:
```
You: Compare Apple, Microsoft, and Google
Agent: [Uses comparative-analysis skill]
       Provides detailed comparison table
```

### 3. risk-analysis

**Purpose**: Comprehensive risk assessment

**When to use**: "how risky", "volatility analysis", "risk level", "beta calculation"

**Capabilities**:
- Volatility measures (standard and downside)
- Beta (market correlation)
- Value at Risk (VaR)
- Sharpe and Sortino ratios
- Maximum drawdown
- Risk categorization (Low/Moderate/High)

**Example**:
```
You: What's the risk profile of Tesla?
Agent: [Uses risk-analysis skill]
       Comprehensive risk report with interpretation
```

## How Skills Work

### 1. Skill Discovery

When you ask a question, Claude:
1. Analyzes your intent
2. Checks available skills (from `.claude/skills/`)
3. Matches your request to appropriate skill(s)
4. Invokes the skill automatically

### 2. Progressive Disclosure

Skills use a three-tier architecture:
- **Tier 1**: Name + description (always loaded)
- **Tier 2**: SKILL.md content (loaded when needed)
- **Tier 3**: Helper scripts (executed by agent)

This keeps context efficient while providing full capability.

### 3. Skill Composition

Claude can use multiple skills together:

```
You: Compare AAPL and TSLA, then tell me which is less risky

Agent's workflow:
1. Uses comparative-analysis skill (compare returns)
2. Uses risk-analysis skill on both stocks
3. Synthesizes results to answer your question
```

## Key Concepts

### Setting Sources

```python
options = ClaudeAgentOptions(
    setting_sources=["project"],  # Load skills from .claude/skills/
    # ...
)
```

**Critical**: The SDK doesn't load filesystem settings by default. You must explicitly enable them.

### Skill Tool

```python
options = ClaudeAgentOptions(
    allowed_tools=["Skill", "Read", "Write", "Bash"],
    # "Skill" must be included!
)
```

The `Skill` tool enables Claude to invoke skills. Without it, skills won't work.

### Working Directory

```python
options = ClaudeAgentOptions(
    cwd=str(project_root),  # Directory containing .claude/
)
```

Skills are discovered relative to the working directory.

## Generated Files

All analysis outputs go to `tmp/`:
- `tmp/aapl_data.json` - Stock lookup results
- `tmp/comparison.json` - Comparative analysis
- `tmp/risk_analysis.json` - Risk assessment
- And more...

These files are:
- Created automatically by skills
- Readable by the agent for follow-up questions
- Gitignored (not committed)
- Easy to inspect manually

## Troubleshooting

### Skills Not Loading

**Problem**: Agent doesn't use skills

**Solution**:
```python
# Check: setting_sources enabled?
options = ClaudeAgentOptions(
    setting_sources=["project"],  # ← Required!
    allowed_tools=["Skill"],      # ← Required!
    cwd="/path/to/project"        # ← Must contain .claude/
)
```

### Helper Scripts Fail

**Problem**: "Module not found" when skill runs

**Solution**:
```bash
# Make sure you're using uv
uv sync
uv run python stock_analyzer.py interactive

# NOT plain python
python stock_analyzer.py  # ❌ May fail
```

### API Key Issues

**Problem**: "API key not found"

**Solution**:
```bash
# Check if .env exists
ls -la .env

# Or use parent project's .env
ls -la ../../../.env

# Verify key is set
echo $CLAUDE_API_KEY  # (or check .env file)
```

### Permission Errors

**Problem**: Can't write to tmp/

**Solution**:
```bash
# Ensure tmp directory exists
mkdir -p tmp

# Check permissions
ls -ld tmp/
```

## Cost Tracking

The application now displays **accurate cost estimates** after each query:

```
────────────────────────────────────────────────────────────
Cost: $0.0856 (estimated) | Input: 18 tokens | Output: 762 tokens
Cache: Write 14381 tokens | Read 67341 tokens
────────────────────────────────────────────────────────────
```

### Why "Estimated"?
The SDK doesn't return cost data, so we calculate based on Claude Sonnet 4.5 pricing:
- Input: $3/M tokens
- Output: $15/M tokens
- Cache write: $3.75/M tokens
- Cache read: $0.30/M tokens

### Prompt Caching Saves 50-70%
The agent heavily uses prompt caching, dramatically reducing costs. Your 2nd, 3rd, 4th queries in the same session cost ~50% less!

**See [COST_TRACKING.md](COST_TRACKING.md) for detailed cost analysis and optimization tips.**

### Typical Costs

| Operation | One-off | Interactive (per turn) |
|-----------|---------|----------------------|
| Stock lookup | $0.03-0.05 | $0.02-0.03 |
| Comparison | $0.06-0.10 | $0.03-0.05 |
| Risk analysis | $0.04-0.08 | $0.02-0.04 |

Interactive mode is more cost-effective for multiple queries!

## Next Steps

After completing Module 2:
- **Module 3**: Hooks and custom validation
- **Module 4**: Subagents for parallel analysis
- **Module 5**: Production deployment patterns

## Key Takeaways

1. **Skills > Scripts**: Reusable capabilities beat one-off code generation
2. **Progressive Disclosure**: Load context only when needed
3. **Filesystem-Based**: Skills are portable across projects
4. **Composable**: Claude combines skills naturally
5. **Production-Ready**: Clean architecture for real applications

## Resources

- [Agent Skills Guide](https://platform.claude.com/docs/en/agent-sdk/skills)
- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/python)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)

## Exercises

Try these challenges:

### Exercise 1: Add a New Skill
Create a `portfolio-optimizer` skill that suggests optimal stock allocations.

### Exercise 2: Customize Analysis
Modify `risk-analysis` to include sector-specific risk benchmarks.

### Exercise 3: Export Features
Add a skill that exports analysis results to PDF or Excel.

### Exercise 4: Real-Time Data
Extend `stock-lookup` to support intraday (real-time) data.

---

**Happy analyzing! 📈**
