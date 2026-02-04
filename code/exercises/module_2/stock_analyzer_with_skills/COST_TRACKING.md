# Cost Tracking Guide

## Overview

The Stock Analyzer now calculates and displays accurate cost estimates for each query, including the benefits of prompt caching.

## Cost Display

After each query, you'll see:

```
────────────────────────────────────────────────────────────
Cost: $0.0856 (estimated) | Input: 18 tokens | Output: 762 tokens
Cache: Write 14381 tokens | Read 67341 tokens
────────────────────────────────────────────────────────────
```

### Why "Estimated"?

The Claude Agent SDK doesn't return actual cost information in the API response. Instead, we calculate costs based on current Claude Sonnet 4.5 pricing:

| Token Type | Cost per Million Tokens |
|------------|------------------------|
| Input | $3.00 |
| Output | $15.00 |
| Cache Write | $3.75 |
| Cache Read | $0.30 |

The calculation is accurate based on these published rates, but actual billing may vary slightly.

## Understanding the Metrics

### Input Tokens
Your prompt and new context. In the example above: **18 tokens**.

This is very small because most context is reused from cache.

### Output Tokens
The agent's response. Example: **762 tokens**.

This is the full response including analysis, text, and formatting.

### Cache Write
Context written to prompt cache. Example: **14,381 tokens**.

This includes:
- System prompt
- Skill definitions (SKILL.md files)
- Tool schemas
- Conversation history

Cached for reuse in subsequent turns (5-minute cache).

### Cache Read
Context read from cache. Example: **67,341 tokens**.

This is reused context from previous interactions. **90% cheaper** than regular input tokens!

## Cost Breakdown Example

For the query above:
```
Input cost:      18 tokens × $3.00 / 1M = $0.000054
Output cost:    762 tokens × $15.00 / 1M = $0.011430
Cache write: 14,381 tokens × $3.75 / 1M = $0.053929
Cache read:  67,341 tokens × $0.30 / 1M = $0.020202
─────────────────────────────────────────────────────────
Total estimated cost: $0.085615 ≈ $0.0856
```

## Why Prompt Caching Matters

### Without Caching
Every token must be sent as input:
```
Input: 81,740 tokens × $3.00 / 1M = $0.24522
Output: 762 tokens × $15.00 / 1M = $0.01143
Total: $0.25665
```

### With Caching (Actual)
Most tokens are cached:
```
Input: 18 tokens × $3.00 / 1M = $0.00005
Output: 762 tokens × $15.00 / 1M = $0.01143
Cache write: 14,381 tokens × $3.75 / 1M = $0.05393
Cache read: 67,341 tokens × $0.30 / 1M = $0.02020
Total: $0.08561
```

**Savings: 67% cheaper due to caching!**

## What Gets Cached?

The Claude Agent SDK automatically caches:
1. **System prompts** - Your instructions to the agent
2. **Skills** - SKILL.md content loaded by the agent
3. **Tool schemas** - Definitions of available tools
4. **Conversation history** - Previous messages in session

Cache TTL: **5 minutes** (ephemeral cache)

## Cost Optimization Tips

### 1. Use Interactive Mode for Follow-ups

Instead of:
```bash
# Each query starts fresh ($0.08+ each)
uv run python stock_analyzer.py query "Analyze AAPL"
uv run python stock_analyzer.py query "Now analyze MSFT"
uv run python stock_analyzer.py query "Compare them"
```

Do this:
```bash
# Single session reuses cache
uv run python stock_analyzer.py interactive
You: Analyze AAPL
You: Now analyze MSFT
You: Compare them
```

**Savings**: 2nd and 3rd queries cost ~50% less due to cache reuse.

### 2. Batch Related Questions

Group related queries in one session:
```bash
uv run python stock_analyzer.py interactive
You: Analyze Tesla stock
You: What's the risk level?
You: How does it compare to Ford?
```

Each follow-up question benefits from cached context.

### 3. Use Skills Efficiently

Skills are loaded on-demand and cached. Once loaded, subsequent uses are cheaper:

**First use**: Loads skill definition (~2000 tokens cached)
**Second use**: Reads from cache (90% cheaper)

### 4. Monitor Cache Metrics

Use `--debug` to see caching in action:
```bash
uv run python stock_analyzer.py query --debug "Analyze AAPL"
```

Look for high cache read numbers - that's money saved!

## Typical Costs

### Query Mode (One-off)
```
Simple lookup: $0.03-0.05
Comparison: $0.06-0.10
Risk analysis: $0.04-0.08
```

### Interactive Mode (5 turns)
```
Turn 1: $0.08 (cache creation)
Turn 2: $0.04 (cache reuse)
Turn 3: $0.04 (cache reuse)
Turn 4: $0.04 (cache reuse)
Turn 5: $0.04 (cache reuse)
Total: $0.24 (average $0.048 per turn)
```

Compare to without caching: **$0.40** (average $0.08 per turn)

## Budget Management

### Set Expectations
For learning/exploration: Budget **$1-2** for extensive use
For production: Monitor costs and set alerts

### Track Your Spending
The cost summary appears after each query. Keep a running total:

```bash
# Quick calculation
echo "0.0856 + 0.0861" | bc  # $0.1717 total
```

### Cost Per Task
- Stock lookup: ~$0.03
- Comparison (2-3 stocks): ~$0.07
- Risk analysis: ~$0.05
- Interactive session (5 turns): ~$0.24

## Debug Mode Benefits

Use `--debug` to see the full breakdown:
```bash
uv run python stock_analyzer.py query --debug "Your question"
```

Shows:
- Raw usage object
- All token counts
- Cache metrics
- Detailed cost calculation

## Why Costs Vary

1. **Response length**: Longer analyses cost more
2. **Cache hits**: More cache reuse = lower cost
3. **Skills used**: Each skill adds context
4. **Conversation length**: More history = more cache

## Summary

- **Actual costs shown**: Based on current pricing
- **Prompt caching**: Reduces costs by 50-70%
- **Interactive mode**: Most cost-effective for multiple queries
- **Monitor**: Check costs after each query
- **Optimize**: Use follow-ups in same session

The estimated costs are accurate and help you understand the real cost of using AI-powered financial analysis!
