# Debug Mode Feature - Summary

## Overview

Added comprehensive debug mode to the Stock Analyzer application, showing the inner workings of agent skills including commands, tool results, and data flow.

## Changes Made

### 1. Updated `stock_analyzer.py`

**Added debug parameter to `print_message()` function**:
- Shows full bash commands (not truncated)
- Displays tool results from script execution
- Shows file contents being read
- Reveals skill arguments
- Displays full file paths

**Updated `query_mode()` function**:
- Added `debug` parameter
- Shows "(Debug mode enabled)" in header
- Passes debug flag to print_message

**Updated `interactive_mode()` function**:
- Added `debug` parameter
- Shows debug status in welcome message
- Passes debug flag to print_message

**Updated argument parsing**:
- Added `--debug` flag to query subparser
- Added `--debug` flag to interactive subparser
- Passes debug value to mode functions

### 2. Documentation Updates

**QUICKSTART.md**:
- Added debug mode examples
- Explained what debug mode shows
- Listed use cases for debug mode

**README.md**:
- Added debug mode section
- Showed usage in both modes
- Listed when to use debug mode

**DEBUG_MODE_EXAMPLES.md** (new file):
- Comprehensive examples of normal vs debug output
- Shows what debug mode reveals
- Use cases: troubleshooting, learning, verification, development
- Complete example session

## Usage

### Query Mode with Debug
```bash
uv run python stock_analyzer.py query --debug "Analyze Tesla stock"
```

### Interactive Mode with Debug
```bash
uv run python stock_analyzer.py interactive --debug
```

## What Debug Mode Shows

### 1. Full Commands
**Before**: `Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output /Users...`

**After**: `Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output /Users/sajal/projects/oreilly/.../tmp/aapl_data.json`

### 2. Tool Results
Shows what scripts output:
```
[Tool Result (truncated)]:
✓ Stock data fetched successfully!
Ticker: TSLA
Period: 6mo
Data points: 127
Current price: $421.96
```

### 3. File Contents
Shows JSON/data being read:
```
[Tool Result (truncated)]:
     1→{
     2→  "ticker": "TSLA",
     3→  "period": "6mo",
     4→  "current_price": 421.96,
     ...
```

### 4. Skill Arguments
Shows what arguments are passed:
```
[Using skill: stock-lookup]
  Args: TSLA
```

### 5. Full File Paths
Shows absolute paths instead of just filenames

## Benefits

1. **Transparency**: See exactly what the agent is doing
2. **Troubleshooting**: Identify issues with commands or paths
3. **Learning**: Understand how skills work internally
4. **Verification**: Check data accuracy and flow
5. **Development**: Test new skills and modifications

## Example Output

```
$ uv run python stock_analyzer.py query --debug "What's the current price of Apple?"

============================================================
STOCK ANALYZER - Query Mode
(Debug mode enabled)
============================================================

Question: What's the current price of Apple?

[Using skill: stock-lookup]
  Args: AAPL

[Tool Result]:
Launching skill: stock-lookup

[Tool: Bash]
  Description: Fetch Apple stock data for last 6 months
  Command: uv run python .claude/skills/stock-lookup/fetch_stock.py --ticker AAPL --period 6mo --output /Users/sajal/.../tmp/aapl_data.json

[Tool Result (truncated)]:
✓ Stock data fetched successfully!
Ticker: AAPL
Period: 6mo
Data points: 127
Current price: $269.48
Price range: $202.49 - $286.19
Output: /Users/.../tmp/aapl_data.json

[Tool: Read]
  File: /Users/sajal/.../tmp/aapl_data.json

[Tool Result (truncated)]:
     1→{
     2→  "ticker": "AAPL",
     3→  "period": "6mo",
     4→  "data_points": 127,
     5→  "current_price": 269.48,
     ...