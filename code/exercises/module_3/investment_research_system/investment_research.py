#!/usr/bin/env python3
"""
Investment Research System - Module 3 Exercise

Multi-agent system for comprehensive stock analysis using:
- Custom tools (in-process MCP servers)
- Pre-built MCP (Tavily Search for news)
- Module 2 Skills (stock-lookup, risk-analysis, comparative-analysis)
- Parallel subagents for research
- Sequential dashboard builder
- Context isolation
- Tool restriction per subagent

Architecture:
    Investment Research Coordinator
         |
         +---> News & Sentiment Subagent (parallel)
         +---> Fundamental Analysis Subagent (parallel)
         +---> Competitive Analysis Subagent (parallel)
         |
         v
    Dashboard Builder Subagent (sequential)
"""

import anyio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)
from claude_agent_sdk.types import StreamEvent

# Import custom tools
from custom_tools.sentiment_tools import sentiment_analyzer, news_aggregator
from custom_tools.financial_tools import financial_metrics_calculator, valuation_assessor
from custom_tools.competitive_tools import sector_benchmark, market_position_analyzer
from custom_tools.visualization_tools import create_chart, build_dashboard

# Import logger
from logger import AgentLogger

# Track progress state
_progress_state = {
    "subagents_spawned": set(),
    "subagents_completed": set(),
    "synthesis_started": False,
    "dashboard_started": False,
    "active_tasks": {},  # Map tool_id to subagent_type
    "text_accumulator": {}  # Accumulate text blocks: {(parent_tool_id, block_index): text}
}

# Find API keys
def find_api_key():
    """Find Anthropic API key from .env files"""
    import os
    from dotenv import load_dotenv

    # Try current directory
    if Path(".env").exists():
        load_dotenv()
        if os.getenv("ANTHROPIC_API_KEY"):
            return os.getenv("ANTHROPIC_API_KEY")

    # Try parent project directory (go up to claude_agent_sdk_course_code)
    # Current: .../code/exercises/module_3/investment_research_system
    # Target:  .../claude_agent_sdk_course_code/.env
    project_root = Path(__file__).parent.parent.parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv("ANTHROPIC_API_KEY")

    return None


def get_tavily_api_key():
    """Get Tavily API key from environment"""
    import os
    from dotenv import load_dotenv

    # Load from .env files
    if Path(".env").exists():
        load_dotenv()

    # Try parent project directory
    project_root = Path(__file__).parent.parent.parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    return os.getenv("TAVILY_API_KEY")


# Create MCP servers for custom tools
def create_mcp_servers():
    """Create in-process MCP servers for each subagent"""

    # Sentiment tools for News & Sentiment subagent
    sentiment_server = create_sdk_mcp_server(
        name="sentiment-tools",
        version="1.0.0",
        tools=[sentiment_analyzer, news_aggregator]
    )

    # Financial tools for Fundamental Analysis subagent
    financial_server = create_sdk_mcp_server(
        name="financial-tools",
        version="1.0.0",
        tools=[financial_metrics_calculator, valuation_assessor]
    )

    # Competitive tools for Competitive Analysis subagent
    competitive_server = create_sdk_mcp_server(
        name="competitive-tools",
        version="1.0.0",
        tools=[sector_benchmark, market_position_analyzer]
    )

    # Visualization tools for Dashboard Builder subagent
    viz_server = create_sdk_mcp_server(
        name="viz-tools",
        version="1.0.0",
        tools=[create_chart, build_dashboard]
    )

    return {
        "sentiment": sentiment_server,
        "financial": financial_server,
        "competitive": competitive_server,
        "viz": viz_server
    }


def configure_external_mcp_servers():
    """
    Configure external MCP servers (like Tavily for web search).

    Returns dict of external MCP server configurations.
    Returns empty dict if API keys not available.
    """
    import os

    external_servers = {}

    # Configure Tavily Search MCP if API key available
    tavily_key = get_tavily_api_key()
    if tavily_key:
        external_servers["tavily"] = {
            "command": "npx",
            "args": ["-y", "tavily-mcp@0.1.3"],
            "env": {"TAVILY_API_KEY": tavily_key}
        }
        print("* Tavily Search MCP configured (tavily-mcp@0.1.3)")
    else:
        print("* Tavily Search not configured (TAVILY_API_KEY not found)")
        print("  News subagent will use custom sentiment tools only")

    return external_servers


def create_options(debug: bool = False, use_module2_path: bool = False, output_session_dir: Path = None):
    """
    Create ClaudeAgentOptions with subagents and custom tools.

    Args:
        debug: Enable debug mode
        use_module2_path: If True, include Module 2 skills path for demonstration
        output_session_dir: Session output directory (default: output/)
    """
    project_root = Path(__file__).parent

    # Set output directories
    if output_session_dir:
        final_output_dir = output_session_dir / "final"
        tmp_output_dir = output_session_dir / "tmp"
    else:
        # Fallback to default structure
        final_output_dir = project_root / "output"
        tmp_output_dir = project_root / "tmp"
        final_output_dir.mkdir(exist_ok=True)
        tmp_output_dir.mkdir(exist_ok=True)

    # Get MCP servers (in-process SDK servers + external servers like Tavily)
    sdk_mcp_servers = create_mcp_servers()
    external_mcp_servers = configure_external_mcp_servers()

    # Combine all MCP servers
    all_mcp_servers = {**sdk_mcp_servers, **external_mcp_servers}

    # Determine which tools news subagent gets (depends on Tavily availability)
    news_tools = ["Read", "Write"]

    # Add Tavily MCP if available
    if "tavily" in external_mcp_servers:
        news_tools.extend([
            "mcp__tavily__tavily-search",
            "mcp__tavily__tavily-extract"
        ])

    # Always add sentiment tools
    news_tools.extend([
        "mcp__sentiment-tools__sentiment_analyzer",
        "mcp__sentiment-tools__news_aggregator"
    ])

    # Define subagents with specific tools and MCP servers
    subagents = {
        "news-sentiment": AgentDefinition(
            description="Analyzes recent news, market sentiment, and media coverage for stocks. Use when you need current events, news analysis, or sentiment assessment.",
            prompt=f"""You are a financial news and sentiment analyst. Your role is to:

1. Search for recent news about the requested company/stock
2. Analyze sentiment of news coverage
3. Identify key themes and trends in media coverage
4. Assess market sentiment (bullish, bearish, neutral)
5. Highlight important events (earnings, product launches, regulatory news)

Tools available:
- Tavily Search MCP (if configured): Search for recent financial news and articles
- sentiment_analyzer: Analyze sentiment of news text
- news_aggregator: Aggregate and categorize news items
- Write: For saving intermediate data to {tmp_output_dir}/ if needed

The coordinator will provide you with the current date for temporal context.
Use this information to focus on recent news (last 7-30 days).

Process:
1. If Tavily is available, search for recent news using the provided date context
2. Analyze sentiment of findings
3. Aggregate themes
4. If you need to save intermediate data, write to {tmp_output_dir}/

Return a concise summary (5-7 bullet points) covering:
- Overall sentiment
- Key news themes
- Recent important events
- Market perception

Keep your analysis focused and avoid overwhelming the main coordinator with raw search results.""",
            tools=news_tools
        ),

        "fundamental-analysis": AgentDefinition(
            description="Performs fundamental financial analysis including valuation metrics, profitability ratios, and financial health assessment. Use when you need deep financial analysis.",
            prompt=f"""You are a fundamental analysis specialist. Your role is to:

1. Gather financial data for the requested stock
2. Calculate key financial metrics (P/E, ROE, profit margins)
3. Assess valuation (overvalued, fairly valued, undervalued)
4. Analyze financial health and profitability
5. Compare against industry standards

Tools available:
- Module 2 Skills (if enabled): stock-lookup, risk-analysis
- financial_metrics_calculator: Calculate financial ratios
- valuation_assessor: Assess valuation
- Write: For saving intermediate data to {tmp_output_dir}/ if needed

Process:
1. Use Module 2 skills to fetch stock data if available
2. Calculate metrics using custom tools
3. Provide valuation assessment
4. If you need to save intermediate data, write to {tmp_output_dir}/

Return a focused summary covering:
- Key financial metrics
- Valuation assessment
- Financial health indicators
- Investment quality rating

Keep analysis concise and actionable.""",
            tools=[
                "Read", "Write", "Bash",
                "Skill",  # Can use Module 2 skills if available
                "mcp__financial-tools__financial_metrics_calculator",
                "mcp__financial-tools__valuation_assessor"
            ]
        ),

        "competitive-analysis": AgentDefinition(
            description="Analyzes competitive positioning, market share, and sector benchmarking. Use when you need to understand a company's competitive landscape.",
            prompt=f"""You are a competitive analysis specialist. Your role is to:

1. Identify key competitors in the sector
2. Benchmark against sector averages
3. Analyze market position and share
4. Assess competitive advantages and weaknesses
5. Compare performance metrics against peers

Tools available:
- Module 2 Skills (if enabled): comparative-analysis
- sector_benchmark: Compare against sector averages
- market_position_analyzer: Analyze market position
- Write: For saving intermediate data to {tmp_output_dir}/ if needed

Process:
1. Identify main competitors
2. Use Module 2 comparative-analysis skill if available
3. Benchmark against sector using custom tools
4. Assess competitive positioning
5. If you need to save intermediate data, write to {tmp_output_dir}/

Return a summary covering:
- Competitive positioning
- Sector ranking
- Key competitive advantages
- Threats from competitors

Focus on strategic insights, not just data.""",
            tools=[
                "Read", "Write", "Bash",
                "Skill",  # Can use Module 2 comparative-analysis
                "mcp__competitive-tools__sector_benchmark",
                "mcp__competitive-tools__market_position_analyzer"
            ]
        ),

        "dashboard-builder": AgentDefinition(
            description="Creates visual dashboards and reports from research findings. Use AFTER all research is complete to visualize results.",
            prompt=f"""You are a data visualization specialist. Your role is to:

1. Take research summaries from all subagents
2. Create charts to visualize key metrics
3. Build a comprehensive HTML dashboard
4. Organize information in a clear, visual format

Tools and Skills available (EXCLUSIVE to you):
- dashboard-design skill: Design guidelines for professional dashboards
- create_chart: Generate interactive charts (bar, line, pie)
- build_dashboard: Assemble complete HTML dashboard
- Write: For saving intermediate data if needed

Output Locations:
- Dashboard file: {final_output_dir}/investment_report_{{ticker}}_{{date}}.html
- Intermediate files: {tmp_output_dir}/ (if needed)

Process:
1. Review all research findings from other subagents
2. Consult dashboard-design skill for best practices
3. Identify key metrics to visualize (returns, metrics, comparisons)
4. Create appropriate charts following design guidelines
5. Assemble everything into a polished HTML dashboard

Dashboard should include:
- Executive summary cards (sentiment, valuation, recommendation)
- News & sentiment section with visualization
- Financial metrics section with charts
- Competitive analysis section with benchmarks
- Overall investment recommendation

Follow dashboard-design skill guidelines for:
- Color scheme (green for positive, red for negative, orange for neutral)
- Chart types (bar for comparisons, line for trends, doughnut for distributions)
- Layout structure and typography
- Professional styling

Make it visually appealing and easy to understand.""",
            tools=[
                "Read", "Write",
                "Skill",  # Can use dashboard-design skill
                "mcp__viz-tools__create_chart",
                "mcp__viz-tools__build_dashboard"
            ]
        ),
    }

    # Base options
    options = ClaudeAgentOptions(
        # Enable partial messages to see subagent streaming events
        include_partial_messages=debug,

        system_prompt=f"""You are an Investment Research Coordinator managing a team of specialized analysts.

Your role:
1. Receive investment research requests for stocks/companies
2. Coordinate parallel research from specialized subagents
3. Synthesize findings into a coherent investment thesis
4. Direct the dashboard builder to visualize results

Session Output Directories:
- Final reports/dashboards: {final_output_dir}/
- Temporary/intermediate files: {tmp_output_dir}/
- Debug logs: logs/session_{{timestamp}}/ (separate directory)

Process:
1. FIRST: Use bash command 'date +"%Y-%m-%d (%B %d, %Y)"' to get the current date

2. Spawn these subagents IN PARALLEL (include current date in each task prompt):
   - news-sentiment: For current news and sentiment (provide date context: "Today is [date]. Search for news from the last 30 days.")
   - fundamental-analysis: For financial metrics and valuation (provide date context for recent data)
   - competitive-analysis: For market position (provide date context)

3. Wait for ALL parallel research to complete

4. Synthesize findings into investment recommendation:
   - Overall sentiment (Positive/Negative/Neutral)
   - Valuation assessment (Overvalued/Fair/Undervalued)
   - Recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)

5. Spawn dashboard-builder subagent SEQUENTIALLY with:
   - All research summaries
   - Your synthesized recommendation
   - Ticker symbol and date

Key principles:
- Get current date FIRST before spawning subagents
- Include date context in all subagent task prompts
- Run research subagents in parallel for speed
- Wait for all research before synthesis
- Dashboard builder runs AFTER research is complete
- Keep your synthesis concise but insightful
- Focus on actionable investment insights""",

        # Include Task tool for spawning subagents
        allowed_tools=["Read", "Write", "Bash", "Task"],

        # Register all MCP servers (subagents will access specific ones)
        mcp_servers=all_mcp_servers,

        # Register subagents
        agents=subagents,

        # Enable skills from .claude/skills/ directory
        setting_sources=["project"],

        # Set working directory
        cwd=str(project_root),

        # Permission mode - bypassPermissions allows subagents to use MCP tools without prompts
        permission_mode="bypassPermissions",

        # Model
        model="sonnet",
    )

    return options


def print_message(message, debug=False, logger=None):
    """Print message based on type"""

    # Handle StreamEvent messages (subagent internal activity)
    if isinstance(message, StreamEvent):
        if debug and logger:
            logger.log_stream_event(message, _progress_state)
        return  # Don't show stream events in console

    # Always show progress indicators (regardless of debug mode)
    logger.show_progress_indicators(message, _progress_state)

    # Debug mode: log to file
    if debug and logger:
        logger.identify_and_log_subagents(message, _progress_state)
        return  # Don't print to console in debug mode

    # Regular debug mode without logger (fallback)
    if debug:
        print(f"\n{'─'*60}")
        print(f"DEBUG: {type(message).__name__}")
        print(f"{'─'*60}")

        # Show message content in detail
        if hasattr(message, 'content'):
            for i, block in enumerate(message.content):
                block_type = type(block).__name__
                print(f"\n  Block {i+1}: {block_type}")

                if hasattr(block, 'text'):
                    print(f"  Text: {block.text[:500]}..." if len(block.text) > 500 else f"  Text: {block.text}")

                if hasattr(block, 'name'):
                    print(f"  Tool: {block.name}")

                if hasattr(block, 'input'):
                    import json
                    input_str = json.dumps(block.input, indent=2)
                    print(f"  Input: {input_str[:500]}..." if len(input_str) > 500 else f"  Input: {input_str}")

                if hasattr(block, 'content') and block_type == 'ToolResultBlock':
                    result_str = str(block.content)
                    print(f"  Result: {result_str[:500]}..." if len(result_str) > 500 else f"  Result: {result_str}")

        if hasattr(message, 'result') and message.result:
            result_str = str(message.result)
            print(f"\n  Result: {result_str[:500]}..." if len(result_str) > 500 else f"  Result: {result_str}")

    # Regular mode: show only assistant text
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        if message.result:
            print(f"\n{'='*60}")
            print("FINAL RESULT:")
            print(f"{'='*60}")
            print(message.result)

            # Cost tracking
            if message.usage:
                usage = message.usage
                print(f"\n{'─'*60}")
                print("Cost Summary:")
                # Handle both dict and object formats
                input_tokens = usage.get('input_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'output_tokens', 0)
                cache_write = usage.get('cache_creation_input_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'cache_creation_input_tokens', 0)
                cache_read = usage.get('cache_read_input_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'cache_read_input_tokens', 0)
                total_cost = usage.get('total_cost_usd', 0) if isinstance(usage, dict) else getattr(usage, 'total_cost_usd', 0)

                if input_tokens:
                    print(f"Input tokens: {input_tokens:,}")
                if output_tokens:
                    print(f"Output tokens: {output_tokens:,}")
                if cache_write:
                    print(f"Cache write: {cache_write:,} tokens")
                if cache_read:
                    print(f"Cache read: {cache_read:,} tokens")
                if total_cost:
                    print(f"Estimated cost: ${total_cost:.4f}")
                print(f"{'─'*60}")


async def query_mode(prompt: str, debug: bool = False):
    """One-shot query mode"""
    print(f"\nInvestment Research Query")
    print(f"{'='*60}\n")

    # Create timestamped session directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Outputs directory structure
    output_session_dir = Path(f"outputs/session_{timestamp}")
    output_session_dir.mkdir(parents=True, exist_ok=True)
    (output_session_dir / "tmp").mkdir(exist_ok=True)
    (output_session_dir / "final").mkdir(exist_ok=True)

    # Always create logger (needed for progress indicators)
    logger = AgentLogger(session_timestamp=timestamp)
    if debug:
        print(f"Debug mode enabled")
        print(f"Session: {timestamp}")
        print(f"  - Logs: logs/session_{timestamp}/")
        print(f"  - Final outputs: {output_session_dir}/final/")
        print(f"  - Temp files: {output_session_dir}/tmp/")
        print(f"{'='*60}\n")

    options = create_options(debug=debug, output_session_dir=output_session_dir)

    async with ClaudeSDKClient(options=options) as client:
        # DIAGNOSTIC: Print available tools for coordinator
        if debug and hasattr(client, 'agent') and hasattr(client.agent, 'tools'):
            print("\n[DIAGNOSTIC] Tools available to coordinator:")
            for tool in client.agent.tools:
                tool_name = getattr(tool, 'name', str(tool))
                print(f"  - {tool_name}")
            print()

        await client.query(prompt)

        async for message in client.receive_response():
            print_message(message, debug=debug, logger=logger)

    # Show log summary if debug mode
    if debug and logger:
        print("\n")
        print(logger.get_summary())


async def interactive_mode(debug: bool = False):
    """Interactive conversation mode"""
    print(f"\nInvestment Research System - Interactive Mode")
    print(f"{'='*60}")
    print("Ask for investment analysis of any stock.")
    print("Examples:")
    print("  - 'Analyze Tesla stock'")
    print("  - 'Give me a comprehensive research report on Apple'")
    print("  - 'Should I invest in Microsoft?'")
    print("\nType 'quit' or 'exit' to end the session.")
    print(f"{'='*60}\n")

    # Create timestamped session directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Outputs directory structure
    output_session_dir = Path(f"outputs/session_{timestamp}")
    output_session_dir.mkdir(parents=True, exist_ok=True)
    (output_session_dir / "tmp").mkdir(exist_ok=True)
    (output_session_dir / "final").mkdir(exist_ok=True)

    # Always create logger (needed for progress indicators)
    logger = AgentLogger(session_timestamp=timestamp)
    if debug:
        print(f"Debug mode enabled")
        print(f"Session: {timestamp}")
        print(f"  - Logs: logs/session_{timestamp}/")
        print(f"  - Final outputs: {output_session_dir}/final/")
        print(f"  - Temp files: {output_session_dir}/tmp/")
        print(f"{'='*60}\n")

    options = create_options(debug=debug, output_session_dir=output_session_dir)

    async with ClaudeSDKClient(options=options) as client:
        # DIAGNOSTIC: Print available tools for coordinator (only once)
        if debug and hasattr(client, 'agent') and hasattr(client.agent, 'tools'):
            print("\n[DIAGNOSTIC] Tools available to coordinator:")
            for tool in client.agent.tools:
                tool_name = getattr(tool, 'name', str(tool))
                print(f"  - {tool_name}")
            print()

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nEnding session. Goodbye!")
                    break

                # Send query
                await client.query(user_input)

                # Receive response
                print("\nAssistant:\n")
                async for message in client.receive_response():
                    print_message(message, debug=debug, logger=logger)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Ending session.")
                break
            except EOFError:
                print("\n\nSession ended.")
                break

    # Show log summary if debug mode
    if debug and logger:
        print("\n")
        print(logger.get_summary())


def main():
    parser = argparse.ArgumentParser(
        description="Investment Research System - Multi-Agent Stock Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query mode - one-shot analysis
  python investment_research.py query "Analyze Tesla stock comprehensively"

  # Interactive mode - conversation
  python investment_research.py interactive

  # Debug mode - see detailed subagent activity
  python investment_research.py query --debug "Research Apple stock"
        """
    )

    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')

    # Query mode
    query_parser = subparsers.add_parser('query', help='One-shot query mode')
    query_parser.add_argument('prompt', type=str, help='Analysis request')
    query_parser.add_argument('--debug', action='store_true', help='Enable debug output')

    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive conversation mode')
    interactive_parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Check API key
    api_key = find_api_key()
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found.")
        print("\nPlease set your API key:")
        print("  1. Create a .env file in this directory")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        print("  Or use the parent project's .env file")
        sys.exit(1)

    # Show mode
    if not args.mode:
        parser.print_help()
        sys.exit(0)

    # Run
    try:
        if args.mode == 'query':
            anyio.run(query_mode, args.prompt, args.debug)
        elif args.mode == 'interactive':
            anyio.run(interactive_mode, args.debug)
    except Exception as e:
        print(f"\nError: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
