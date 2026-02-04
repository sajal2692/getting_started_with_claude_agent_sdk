# Module 1: Stock & Company News Analyzer

## Overview

This module demonstrates the Claude Agent SDK's "code generation for non-coding" philosophy through financial analysis exercises. You'll build agents that write and execute Python code to analyze stock data.

## Setup

### 1. Navigate to this directory

```bash
cd notebooks/exercises/module_1
```

### 2. Install dependencies with uv

This module has its own self-contained environment:

```bash
uv sync
```

This will install:
- claude-agent-sdk
- yfinance (for stock data)
- pandas (for data analysis)
- matplotlib (for visualization)
- jupyter (for notebooks)

### 3. Configure API key

Option A - Use parent project's .env (recommended):
```bash
# The notebook will automatically use ../../../.env if present
```

Option B - Create local .env:
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### 4. Launch Jupyter

**Important**: Start Jupyter from this directory so agents run in the correct context:

```bash
uv run jupyter notebook
```

Then open `01_stock_analyzer.ipynb`

## Project Structure

```
module_1/
├── pyproject.toml              # uv dependencies for this module
├── .env.example                # Template for API key
├── .gitignore                  # Ignore .venv, tmp/, etc.
├── tmp/                        # Generated files (scripts, data, results)
│   └── .gitkeep
├── 01_stock_analyzer.ipynb     # Main exercise notebook
└── README.md                   # This file
```

## How It Works

### Agent Execution Model

1. **Working Directory**: Agents run from `module_1/` directory
2. **Package Management**: Uses `uv run python` to execute scripts
3. **File Storage**: All generated files go to `tmp/` subdirectory
4. **Environment**: Self-contained uv environment with all dependencies

### System Prompt Instructions

Each exercise configures the agent with clear instructions:

```python
system_prompt="""You are a financial analysis assistant.

IMPORTANT:
- Use `uv run python` to execute Python scripts
- Save all files to `tmp/` subdirectory
- All packages (yfinance, pandas, etc.) are pre-installed via uv"""
```

This ensures the agent:
- ✅ Uses uv to run Python (not plain `python`)
- ✅ Saves files to the correct location
- ✅ Doesn't try to install packages with pip

## Exercises

### Part 1: Using `query()` for Single-Shot Analysis
- **Exercise 1A**: Basic stock analysis (AAPL)
- **Exercise 1B**: Multi-stock comparison

### Part 2: Using `ClaudeSDKClient` for Interactive Sessions
- **Exercise 2A**: Multi-turn Tesla analysis with context

### Part 3: Advanced Tool Configuration
- **Exercise 3A**: Read-only mode restrictions

### Part 4: Real-World Application
- **Exercise 4**: Complete portfolio analyzer

## Generated Files

Check the `tmp/` directory after running exercises to see:
- Python scripts written by the agent
- Stock data (JSON, CSV)
- Analysis results
- Visualizations (if generated)

## Troubleshooting

### Issue: Module not found errors

**Cause**: Running from wrong directory or uv environment not synced

**Solution**:
```bash
# Make sure you're in module_1
pwd  # Should end with: /module_1

# Resync dependencies
uv sync

# Launch Jupyter from this directory
uv run jupyter notebook
```

### Issue: API key not found

**Cause**: No .env file present

**Solution**:
```bash
# Option 1: Use parent project's .env (recommended)
# Just ensure ../../../.env exists with ANTHROPIC_API_KEY

# Option 2: Create local .env
cp .env.example .env
# Edit .env and add your key
```

### Issue: Agent tries to use pip

**Cause**: System prompt not being applied

**Solution**: Check that `system_prompt` is set in `ClaudeAgentOptions` - this is already configured in all exercises.

### Issue: Files created in wrong location

**Cause**: Working directory not set correctly

**Solution**: Each exercise sets `cwd=str(Path.cwd())` - make sure you launched Jupyter from the `module_1` directory.

## Expected Costs

Module 1 exercises typically cost:
- Exercise 1A: ~$0.05-0.10
- Exercise 1B: ~$0.10-0.15
- Exercise 2A: ~$0.15-0.20
- Exercise 4: ~$0.20-0.30

**Total**: Approximately $0.50-0.75 for all exercises

## Next Steps

After completing Module 1, proceed to Module 2 which covers:
- Session management and resumption
- Hooks for custom workflow logic
- Agent skills for reusable capabilities

## Resources

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/python)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [uv Documentation](https://docs.astral.sh/uv/)
