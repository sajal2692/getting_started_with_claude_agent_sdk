#!/usr/bin/env python3
"""
Stock Analyzer with Agent Skills

A financial analysis assistant powered by Claude Agent SDK with custom skills.

Modes:
  - query: One-off questions
  - interactive: Chat-based conversation

Examples:
  python stock_analyzer.py query "Analyze Apple stock performance"
  python stock_analyzer.py interactive
"""

import argparse
import sys
from pathlib import Path

import anyio
from dotenv import load_dotenv

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# Load environment variables
load_dotenv()


def get_project_paths():
    """Get absolute paths for the project"""
    project_root = Path(__file__).parent.absolute()
    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    return {
        "project_root": str(project_root),
        "tmp_dir": str(tmp_dir),
    }


def create_agent_options() -> ClaudeAgentOptions:
    """Create standard agent options with skills enabled"""
    paths = get_project_paths()

    return ClaudeAgentOptions(
        # Enable project skills from .claude/skills/
        setting_sources=["project"],

        # Include Skill tool + analysis tools
        allowed_tools=["Skill", "Read", "Write", "Bash"],

        # Set working directory to project root
        cwd=paths["project_root"],

        # Auto-approve tool usage for smooth experience
        permission_mode="bypassPermissions",

        # Use Sonnet for cost-effectiveness
        model="claude-sonnet-4-5",

        # Reasonable turn limit
        max_turns=20,

        # System prompt with context
        system_prompt=f"""You are a financial analysis assistant with specialized skills.

IMPORTANT INSTRUCTIONS:
1. **Skills Available**: You have three custom skills:
   - stock-lookup: Fetch historical stock data for any ticker
   - comparative-analysis: Compare multiple stocks side-by-side
   - risk-analysis: Analyze volatility, beta, and risk metrics

2. **When to Use Skills**:
   - User asks about a specific stock → Use stock-lookup skill
   - User wants to compare stocks → Use comparative-analysis skill
   - User asks about risk/volatility → Use risk-analysis skill

3. **File Operations**:
   - Working directory: {paths['project_root']}
   - Save all outputs to: {paths['tmp_dir']}/
   - Use absolute paths: {paths['tmp_dir']}/filename
   - DO NOT use /tmp - use the tmp/ subdirectory

4. **Package Management**:
   - Use `uv run python` to execute Python scripts
   - All packages (yfinance, pandas, etc.) are pre-installed

5. **Communication Style**:
   - Be conversational and helpful
   - Explain financial concepts clearly
   - Provide actionable insights
   - Use the skills to avoid writing repetitive code

Your goal is to help users make informed investment decisions through data-driven analysis."""
    )


def print_message(message, debug=False):
    """Pretty print agent messages

    Args:
        message: The message to print
        debug: If True, show detailed tool results and outputs
    """
    msg_type = type(message).__name__

    if msg_type == "SystemMessage":
        # Skip system messages
        pass

    elif msg_type == "AssistantMessage":
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"\nAssistant: {block.text}")

            elif isinstance(block, ToolUseBlock):
                # Show when skills are activated
                if block.name == "Skill":
                    skill_name = block.input.get("skill", "unknown")
                    print(f"\n[Using skill: {skill_name}]")

                    if debug:
                        # Show skill arguments in debug mode
                        args = block.input.get("args", "")
                        if args:
                            print(f"  Args: {args}")

                elif block.name == "Bash":
                    # Show bash commands with full details
                    command = block.input.get("command", "")
                    description = block.input.get("description", "")

                    print(f"\n[Tool: Bash]")
                    if description:
                        print(f"  Description: {description}")

                    # Show command (truncate if very long, unless debug)
                    if debug:
                        print(f"  Command: {command}")
                    elif len(command) > 100:
                        print(f"  Command: {command[:100]}...")
                    else:
                        print(f"  Command: {command}")

                elif block.name == "Read":
                    # Show Read tool usage
                    file_path = block.input.get("file_path", "")
                    print(f"\n[Tool: Read]")
                    if debug:
                        print(f"  File: {file_path}")
                    else:
                        # Show just the filename
                        from pathlib import Path
                        print(f"  File: {Path(file_path).name}")

                else:
                    # Show other tool usage briefly
                    if "description" in block.input:
                        print(f"\n[Tool: {block.name} - {block.input['description']}]")
                    elif debug:
                        print(f"\n[Tool: {block.name}]")
                        print(f"  Input: {block.input}")

    elif msg_type == "UserMessage":
        # Show tool results
        for block in message.content:
            if hasattr(block, 'is_error') and block.is_error:
                print(f"\n[Error: {block.content}]")
            elif debug:
                # In debug mode, show tool results
                if hasattr(block, 'content'):
                    content = str(block.content)

                    # Show first part of output
                    if len(content) > 500:
                        print(f"\n[Tool Result (truncated)]:")
                        print(content[:500])
                        print(f"... ({len(content) - 500} more characters)")
                    else:
                        print(f"\n[Tool Result]:")
                        print(content)

    elif msg_type == "ResultMessage":
        # Show cost summary
        if hasattr(message, 'usage') and message.usage:
            usage = message.usage

            # Debug: Show raw usage object
            if debug:
                print(f"\n[Debug - Raw Usage Object]:")
                if isinstance(usage, dict):
                    print(f"  Type: dict")
                    print(f"  Keys: {list(usage.keys())}")
                    print(f"  Content: {usage}")
                else:
                    print(f"  Type: {type(usage).__name__}")
                    print(f"  Attributes: {dir(usage)}")
                    print(f"  Content: {usage}")

            # Handle both dict and object formats
            if isinstance(usage, dict):
                total_cost = usage.get('total_cost_usd', 0)
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                cache_creation = usage.get('cache_creation_input_tokens', 0)
                cache_read = usage.get('cache_read_input_tokens', 0)
            else:
                total_cost = getattr(usage, 'total_cost_usd', 0)
                input_tokens = getattr(usage, 'input_tokens', 0)
                output_tokens = getattr(usage, 'output_tokens', 0)
                cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)
                cache_read = getattr(usage, 'cache_read_input_tokens', 0)

            print(f"\n{'─'*60}")

            # Calculate cost manually if not provided
            if total_cost == 0 and (input_tokens > 0 or output_tokens > 0):
                # Claude Sonnet 4.5 pricing (as of 2026)
                # Input: $3 per million tokens
                # Output: $15 per million tokens
                # Cache write: $3.75 per million tokens
                # Cache read: $0.30 per million tokens

                input_cost = (input_tokens / 1_000_000) * 3.0
                output_cost = (output_tokens / 1_000_000) * 15.0
                cache_write_cost = (cache_creation / 1_000_000) * 3.75
                cache_read_cost = (cache_read / 1_000_000) * 0.30

                estimated_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

                print(f"Cost: ${estimated_cost:.4f} (estimated) | "
                      f"Input: {input_tokens} tokens | "
                      f"Output: {output_tokens} tokens")

                if cache_creation > 0 or cache_read > 0:
                    print(f"Cache: Write {cache_creation} tokens | Read {cache_read} tokens")
            else:
                print(f"Cost: ${total_cost:.4f} | "
                      f"Input: {input_tokens} tokens | "
                      f"Output: {output_tokens} tokens")

                if cache_creation > 0 or cache_read > 0:
                    print(f"Cache: Write {cache_creation} tokens | Read {cache_read} tokens")

            print(f"{'─'*60}")


async def query_mode(question: str, debug: bool = False):
    """One-off query mode"""
    print(f"\n{'='*60}")
    print("STOCK ANALYZER - Query Mode")
    if debug:
        print("(Debug mode enabled)")
    print(f"{'='*60}")
    print(f"\nQuestion: {question}\n")

    options = create_agent_options()

    async for message in query(prompt=question, options=options):
        print_message(message, debug=debug)


async def interactive_mode(debug: bool = False):
    """Interactive chat mode"""
    print(f"\n{'='*60}")
    print("STOCK ANALYZER - Interactive Mode")
    if debug:
        print("(Debug mode enabled)")
    print(f"{'='*60}")
    print("\nWelcome to the Stock Analyzer!")
    print("\nAvailable skills:")
    print("  • stock-lookup: Get historical data for any stock")
    print("  • comparative-analysis: Compare multiple stocks")
    print("  • risk-analysis: Analyze volatility and risk")
    print("\nType 'quit' or 'exit' to end the session.")
    if debug:
        print("Debug mode shows tool commands and results.")
    print(f"{'='*60}\n")

    options = create_agent_options()

    async with ClaudeSDKClient(options=options) as client:
        turn_number = 0

        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nSession ended. Goodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'done']:
                print("\nSession ended. Goodbye!")
                break

            turn_number += 1

            # Send query to agent
            await client.query(user_input)

            # Stream response
            async for message in client.receive_response():
                print_message(message, debug=debug)

            print()  # Add spacing between turns


def main():
    parser = argparse.ArgumentParser(
        description="Stock Analyzer with Agent Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-off query
  python stock_analyzer.py query "Analyze Tesla stock performance"
  python stock_analyzer.py query "Compare AAPL, MSFT, and GOOGL"
  python stock_analyzer.py query "What's the risk level of Bitcoin stocks?"

  # Interactive mode
  python stock_analyzer.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Query mode
    query_parser = subparsers.add_parser(
        "query",
        help="One-off question mode"
    )
    query_parser.add_argument(
        "question",
        help="Your question about stocks"
    )
    query_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (show tool commands and results)"
    )

    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Interactive chat mode"
    )
    interactive_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (show tool commands and results)"
    )

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        sys.exit(1)

    # Run the appropriate mode
    try:
        if args.mode == "query":
            anyio.run(query_mode, args.question, args.debug)
        elif args.mode == "interactive":
            anyio.run(interactive_mode, args.debug)
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
