# Debug Mode Examples

## Overview

Debug mode shows the inner workings of the agent, including exact commands, tool results, and data flow. This is invaluable for understanding how skills work and troubleshooting issues.

## Enabling Debug Mode

```bash
# Query mode with debug
uv run python stock_analyzer.py query --debug "Your question"

# Interactive mode with debug
uv run python stock_analyzer.py interactive --debug
```

## What Debug Mode Shows

### 1. Full Commands (Not Truncated)

**Normal**: `Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output /Users...`

**Debug**: `Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output /Users/sajal/projects/oreilly/claude_agent_sdk_course/claude_agent_sdk_course_code/notebooks/exercises/module_2/stock_analyzer_with_skills/tmp/aapl_data.json`

### 2. Tool Results

**Normal**: (hidden)

**Debug**:
```
[Tool Result (truncated)]:
✓ Stock data fetched successfully!
Ticker: AAPL
Period: 6mo
Data points: 127
Current price: $269.48
Price range: $202.49 - $286.19
Output: /Users/.../tmp/aapl_data.json
```

### 3. File Contents

**Normal**: (hidden)

**Debug**:
```
[Tool Result (truncated)]:
     1→{
     2→  "ticker": "AAPL",
     3→  "period": "6mo",
     4→  "data_points": 127,
     5→  "date_range": {
     6→    "start": "2025-08-04",
     7→    "end": "2026-02-03"
     8→  },
     9→  "current_price": 269.48,
    10→  "statistics": {
    11→    "mean": 255.62,
    12→    "min": 202.49,
    13→    "max": 286.19,
    14→    "std_dev": 18.51,
    15→    "volatility_pct": 7.24
    16→  },
    ...
```

### 4. Skill Arguments

**Normal**: `[Using skill: stock-lookup]`

**Debug**:
```
[Using skill: stock-lookup]
  Args: AAPL
```

### 5. Full File Paths

**Normal**: `File: aapl_data.json`

**Debug**: `File: /Users/sajal/projects/.../tmp/aapl_data.json`

## When to Use Debug Mode

### Troubleshooting

```bash
# Skill not working? See what command is being run
uv run python stock_analyzer.py query --debug "Analyze XYZ stock"

# Check: Is the command correct?
# Check: Are the file paths absolute?
# Check: Is the script returning errors?
```

### Learning

```bash
# See exactly how skills work
uv run python stock_analyzer.py query --debug "Compare AAPL and MSFT"

# Observe:
# - Which helper script is called
# - What arguments are passed
# - What data is returned
# - How the agent processes results
```

### Verification

```bash
# Verify data accuracy
uv run python stock_analyzer.py query --debug "Risk analysis for Tesla"

# Check:
# - What data was fetched
# - What calculations were performed
# - What file contains the results
```

### Development

```bash
# Testing new skills
uv run python stock_analyzer.py interactive --debug

# Monitor:
# - Skill activation
# - Command execution
# - Error messages
# - Output format
```

## Example Session

```bash
$ uv run python stock_analyzer.py query --debug "What's Tesla's current price?"

============================================================
STOCK ANALYZER - Query Mode
(Debug mode enabled)
============================================================

Question: What's Tesla's current price?

[Using skill: stock-lookup]
  Args: TSLA

[Tool Result]:
Launching skill: stock-lookup

[Tool: Bash]
  Description: Fetch Tesla stock data for last 6 months
  Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker TSLA --period 6mo --output /Users/sajal/projects/oreilly/claude_agent_sdk_course/claude_agent_sdk_course_code/notebooks/exercises/module_2/stock_analyzer_with_skills/tmp/tsla_data.json

[Tool Result (truncated)]:
✓ Stock data fetched successfully!
Ticker: TSLA
Period: 6mo
Data points: 127
Current price: $421.96
Price range: $308.72 - $489.88
...

[Tool: Read]
  File: /Users/sajal/.../tmp/tsla_data.json

[Tool Result (truncated)]:
     1→{
     2→  "ticker": "TSLA",
     3→  "period": "6mo",
     4→  "data_points": 127,
     5→  "current_price": 421.96,
     ...