# Module 1: Stock & Company News Analyzer

A Jupyter notebook-based introduction to the Claude Agent SDK. Agents write and execute Python code to analyze stock data using yfinance.

## Project Structure

```
stock_analyzer/
├── pyproject.toml              # Dependencies
├── .env.example                # Optional API-key template
├── tmp/                        # Generated files (scripts, data, results)
├── 01_stock_analyzer.ipynb     # Main exercise notebook
└── README.md
```

## Setup

1. Navigate to this directory:
```bash
cd code/exercises/module_1/stock_analyzer
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

4. Launch Jupyter:
```bash
uv run jupyter notebook
```

5. Open `01_stock_analyzer.ipynb` and run the exercises

## Expected Output

After running exercises, the `tmp/` directory will contain:
- Python scripts written by the agent
- Stock data files (JSON, CSV)
- Analysis results
- Visualizations (charts, if generated)

Example agent behavior:
- Writes Python scripts using yfinance to fetch stock data
- Executes scripts with `uv run python`
- Analyzes data and provides insights
- Saves results to `tmp/` directory
