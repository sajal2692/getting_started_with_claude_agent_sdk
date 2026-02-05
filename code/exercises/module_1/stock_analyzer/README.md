# Module 1: Stock & Company News Analyzer

A Jupyter notebook-based introduction to the Claude Agent SDK. Agents write and execute Python code to analyze stock data using yfinance.

## Project Structure

```
stock_analyzer/
├── pyproject.toml              # Dependencies
├── .env.example                # API key template
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

3. Configure API key (choose one):
```bash
# Option A: Use parent project's .env (recommended)
# The notebook will automatically use ../../../../.env if present

# Option B: Create local .env
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
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
