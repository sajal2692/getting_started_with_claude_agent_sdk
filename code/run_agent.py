#!/usr/bin/env python3
"""
Simple CLI wrapper for Claude Agent SDK.
Takes a prompt string and executes a one-off agent query.

Usage:
    python run_agent.py "What files are in this directory?"
    python run_agent.py "Review the code in main.py"
"""

import asyncio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions


def print_message(message):
    """Pretty print agent messages."""
    msg_type = type(message).__name__

    if msg_type == "SystemMessage":
        # Skip system messages for cleaner output
        pass

    elif msg_type == "AssistantMessage":
        # Print assistant thinking and tool use
        if hasattr(message, 'content'):
            for block in message.content:
                block_type = type(block).__name__
                if block_type == "TextBlock":
                    print(f"🤖 Assistant: {block.text}")
                elif block_type == "ToolUseBlock":
                    print(f"🔧 Tool: {block.name}")
                    if hasattr(block, 'input'):
                        # Show description first if available
                        if 'description' in block.input:
                            print(f"   → {block.input['description']}")

    elif msg_type == "UserMessage":
        # Print tool results
        if hasattr(message, 'content'):
            for block in message.content:
                block_type = type(block).__name__
                if block_type == "ToolResultBlock":
                    if block.is_error:
                        print(f"❌ Tool Error: {block.content}")
                    # Skip showing tool results for cleaner output

    elif msg_type == "ResultMessage":
        # Show cost and timing metadata
        if hasattr(message, 'total_cost_usd') and hasattr(message, 'duration_ms'):
            print(f"\n💰 Cost: ${message.total_cost_usd:.4f} | ⏱️ Time: {message.duration_ms/1000:.1f}s")


async def run_agent(prompt: str):
    """Execute a one-off agent query with the given prompt."""

    # Configure agent with Claude Code system prompt for better behavior
    options = ClaudeAgentOptions(
        system_prompt="claude_code",
        permission_mode="bypassPermissions"  # Auto-approve tools for convenience
    )

    # Stream messages and print them
    async for message in query(prompt=prompt, options=options):
        print_message(message)


def main():
    """Main entry point."""
    # Check if prompt was provided
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py <prompt>")
        print("\nExamples:")
        print('  python run_agent.py "What files are in this directory?"')
        print('  python run_agent.py "Review the code in main.py"')
        sys.exit(1)

    # Get the prompt from command line arguments
    prompt = " ".join(sys.argv[1:])

    print(f"📝 Prompt: {prompt}\n")

    # Run the agent
    asyncio.run(run_agent(prompt))


if __name__ == "__main__":
    main()
