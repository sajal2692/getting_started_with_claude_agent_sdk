# Quick Start Guide

## Setup (2 minutes)

```bash
# 1. Navigate to directory
cd notebooks/exercises/module_2/stock_analyzer_with_skills

# 2. Install dependencies
uv sync

# 3. Configure API key (choose one)
# Option A: Use parent .env (recommended)
ls ../../../.env  # Should exist

# Option B: Create local .env
cp .env.example .env
# Edit .env: CLAUDE_API_KEY=your_key_here
```

## Usage

### One-Off Queries

```bash
# Basic analysis
uv run python stock_analyzer.py query "Analyze Apple stock"

# Comparison
uv run python stock_analyzer.py query "Compare AAPL, MSFT, and GOOGL"

# Risk assessment
uv run python stock_analyzer.py query "How risky is Tesla?"

# Complex multi-skill query
uv run python stock_analyzer.py query "Compare Netflix and Disney, then tell me which is less risky"

# Debug mode (see tool commands and results)
uv run python stock_analyzer.py query --debug "What's the current price of Apple?"
```

### Interactive Chat

```bash
uv run python stock_analyzer.py interactive

# Then chat naturally:
You: Look up Tesla stock for the last year
You: How does it compare to Ford?
You: What's the volatility?
You: quit

# Debug mode for interactive
uv run python stock_analyzer.py interactive --debug
```

### Debug Mode

Add `--debug` flag to see:
- Exact commands executed by skills
- Tool results and outputs
- Full file paths
- JSON data read by agent

This is helpful for:
- Understanding what the agent is doing
- Troubleshooting issues
- Learning how skills work
- Verifying data accuracy

## Skills Available

| Skill | Trigger Words | What It Does |
|-------|--------------|--------------|
| **stock-lookup** | "look up", "analyze", "get data for" | Fetches historical stock data |
| **comparative-analysis** | "compare", "vs", "which is better" | Compares multiple stocks |
| **risk-analysis** | "risk", "volatility", "how safe" | Analyzes risk metrics |

## Example Queries

**Stock Lookup**:
```bash
uv run python stock_analyzer.py query "Analyze Microsoft stock over the last 2 years"
```

**Comparison**:
```bash
uv run python stock_analyzer.py query "Compare tech stocks: AAPL, GOOGL, MSFT, META"
```

**Risk Assessment**:
```bash
uv run python stock_analyzer.py query "What's the risk profile of GameStop (GME)?"
```

**Multi-Skill**:
```bash
uv run python stock_analyzer.py query "Compare TSLA and F, analyze risk for both, recommend for conservative investor"
```

## Output Files

Check `tmp/` directory for generated files:
```bash
ls -lh tmp/
```

You'll find:
- `*_data.json` - Stock lookup results
- `comparison_*.json` - Comparative analysis
- `*_risk.json` - Risk assessments

## Troubleshooting

**Skills not loading?**
```bash
# Verify .claude/skills/ exists
ls -la .claude/skills/

# Check skills are valid
cat .claude/skills/stock-lookup/SKILL.md
```

**Module not found?**
```bash
# Reinstall dependencies
rm -rf .venv
uv sync
```

**API key errors?**
```bash
# Check .env file
cat .env

# Or verify parent .env
cat ../../../.env
```

## Tips

1. **Interactive mode is best** for exploratory analysis
2. **Query mode is faster** for specific questions
3. **Skills compose naturally** - ask complex multi-part questions
4. **Check tmp/ files** to see what the agent generated
5. **Use absolute paths** if referencing output files

## Cost Tracking

The app now shows **accurate cost estimates** after each query:
```
Cost: $0.0856 (estimated) | Input: 18 tokens | Output: 762 tokens
Cache: Write 14381 tokens | Read 67341 tokens
```

**Prompt caching saves 50-70%!** Follow-up questions in interactive mode cost much less.

Typical costs:
- Stock lookup: $0.03-0.05
- Comparison (2-3 stocks): $0.06-0.10
- Risk analysis: $0.04-0.08
- Interactive session (5 turns): ~$0.24 total

See [COST_TRACKING.md](COST_TRACKING.md) for detailed analysis.

## Next Steps

- Try all three skills
- Ask multi-skill questions
- Explore interactive mode
- Check generated files in tmp/
- Customize skills (edit SKILL.md files)

---

**Happy analyzing! 📈**
