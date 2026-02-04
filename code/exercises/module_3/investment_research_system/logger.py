"""
Logging utilities for multi-agent system.

Handles parallel subagent logging with proper organization and timestamps.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import threading


class AgentLogger:
    """Thread-safe logger for multi-agent system."""

    def __init__(self, session_timestamp: str = None):
        """
        Initialize logger.

        Args:
            session_timestamp: Timestamp string for this session (e.g., "20260204_174812")
                              If provided, logs go to logs/session_{timestamp}/
                              Otherwise, logs go to logs/
        """
        if session_timestamp:
            self.log_dir = Path("logs") / f"session_{session_timestamp}"
        else:
            self.log_dir = Path("logs")

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.session_timestamp = session_timestamp

        # Create session log file with timestamp
        timestamp = session_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_dir / f"session_{timestamp}.log"
        self.session_file.touch()

        # Track subagent logs
        self.subagent_logs = {}

    def log_event(self, event_type: str, data: Dict[str, Any], subagent: str = "coordinator"):
        """
        Log an event to the appropriate log file.

        Args:
            event_type: Type of event (e.g., "subagent_spawn", "tool_call", "result")
            data: Event data
            subagent: Which agent this event is from (default: "coordinator")
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "subagent": subagent,
            "event_type": event_type,
            "data": data
        }

        # Thread-safe file writing
        with self.lock:
            # Write to session log
            with open(self.session_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            # Also write to subagent-specific log
            if subagent != "coordinator":
                subagent_file = self.log_dir / f"subagent_{subagent}_{self.session_file.stem}.log"
                with open(subagent_file, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")

    def log_message(self, message: Any, subagent: str = "coordinator"):
        """Log a message from the SDK."""
        message_type = type(message).__name__

        if message_type == "AssistantMessage":
            self._log_assistant_message(message, subagent)
        elif message_type == "UserMessage":
            self._log_user_message(message, subagent)
        elif message_type == "ResultMessage":
            self._log_result_message(message, subagent)

    def _log_assistant_message(self, message, subagent: str):
        """Log AssistantMessage with tool calls and responses."""
        if not hasattr(message, 'content'):
            return

        for i, block in enumerate(message.content):
            block_type = type(block).__name__

            if block_type == "TextBlock":
                self.log_event(
                    "assistant_text",
                    {
                        "text": block.text,
                        "length": len(block.text)
                    },
                    subagent
                )

            elif block_type == "ToolUseBlock":
                tool_data = {
                    "tool_name": getattr(block, 'name', 'unknown'),
                    "tool_id": getattr(block, 'id', 'unknown'),
                    "input": getattr(block, 'input', {})
                }
                self.log_event("tool_call", tool_data, subagent)

            elif block_type == "ToolResultBlock":
                result_content = getattr(block, 'content', '')
                result_str = str(result_content)

                self.log_event(
                    "tool_result",
                    {
                        "tool_id": getattr(block, 'tool_use_id', 'unknown'),
                        "result": result_str[:1000],  # Truncate for logs
                        "result_length": len(result_str),
                        "truncated": len(result_str) > 1000
                    },
                    subagent
                )

    def _log_user_message(self, message, subagent: str):
        """Log user input."""
        if hasattr(message, 'content'):
            content_str = str(message.content)
            self.log_event(
                "user_input",
                {
                    "content": content_str,
                    "length": len(content_str)
                },
                subagent
            )

    def _log_result_message(self, message, subagent: str):
        """Log final result with usage stats."""
        data = {}

        if hasattr(message, 'result') and message.result:
            data["result"] = str(message.result)[:500]
            data["result_length"] = len(message.result)

        if hasattr(message, 'usage') and message.usage:
            usage = message.usage
            if isinstance(usage, dict):
                data["usage"] = usage
            else:
                data["usage"] = {
                    "input_tokens": getattr(usage, 'input_tokens', 0),
                    "output_tokens": getattr(usage, 'output_tokens', 0),
                    "cache_write": getattr(usage, 'cache_creation_input_tokens', 0),
                    "cache_read": getattr(usage, 'cache_read_input_tokens', 0),
                    "total_cost_usd": getattr(usage, 'total_cost_usd', 0)
                }

        self.log_event("final_result", data, subagent)

    def log_subagent_spawn(self, subagent_name: str, description: str):
        """Log when a subagent is spawned."""
        self.log_event(
            "subagent_spawn",
            {
                "subagent": subagent_name,
                "description": description
            },
            "coordinator"
        )

    def log_subagent_complete(self, subagent_name: str, summary: str):
        """Log when a subagent completes."""
        self.log_event(
            "subagent_complete",
            {
                "subagent": subagent_name,
                "summary": summary
            },
            "coordinator"
        )

    def get_subagent_text_blocks(self, subagent_name: str = None) -> list:
        """
        Get all complete text blocks from subagents.

        Args:
            subagent_name: Filter by specific subagent (e.g., "news-sentiment")
                          If None, returns all text blocks from all subagents

        Returns:
            List of dicts with: {subagent, text, timestamp}
        """
        text_blocks = []

        with open(self.session_file, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "subagent_text_complete":
                        subagent = event.get("subagent", "unknown")

                        # Filter by subagent name if specified
                        if subagent_name and subagent != subagent_name:
                            continue

                        text_blocks.append({
                            "subagent": subagent,
                            "text": event.get("data", {}).get("text", ""),
                            "timestamp": event.get("timestamp", ""),
                            "text_length": event.get("data", {}).get("text_length", 0)
                        })
                except:
                    continue

        return text_blocks

    def get_summary(self) -> str:
        """Generate a human-readable summary of the session."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"Session Log Summary: {self.session_file.name}")
        lines.append("=" * 80)

        # Read all log entries
        events = []
        with open(self.session_file, "r") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue

        # Count events by type and subagent
        by_type = {}
        by_agent = {}

        for event in events:
            event_type = event.get("event_type", "unknown")
            subagent = event.get("subagent", "unknown")

            by_type[event_type] = by_type.get(event_type, 0) + 1
            by_agent[subagent] = by_agent.get(subagent, 0) + 1

        lines.append("\nEvents by Type:")
        for event_type, count in sorted(by_type.items()):
            lines.append(f"  {event_type}: {count}")

        lines.append("\nEvents by Agent:")
        for agent, count in sorted(by_agent.items()):
            lines.append(f"  {agent}: {count}")

        # Show subagent activity
        subagent_spawns = [e for e in events if e.get("event_type") == "subagent_spawn"]
        subagent_results = [e for e in events if e.get("event_type") == "subagent_result"]
        subagent_tool_calls = [e for e in events if e.get("event_type") == "subagent_tool_call"]
        subagent_text_blocks = [e for e in events if e.get("event_type") == "subagent_text_complete"]

        if subagent_spawns or subagent_results or subagent_tool_calls or subagent_text_blocks:
            lines.append(f"\n{'='*80}")
            lines.append(f"SUBAGENT ACTIVITY (with internal messages)")
            lines.append(f"{'='*80}")

        if subagent_spawns:
            lines.append(f"\nSubagents Spawned: {len(subagent_spawns)}")
            for i, spawn in enumerate(subagent_spawns, 1):
                data = spawn.get("data", {})
                subagent_type = data.get("subagent_type", "unknown")
                prompt_preview = data.get("prompt_preview", "")
                tool_id = data.get("tool_id", "unknown")

                lines.append(f"\n  {i}. {subagent_type}")
                lines.append(f"     Tool ID: {tool_id}")
                if prompt_preview:
                    lines.append(f"     Task: {prompt_preview}...")

        # Show internal tool calls made by subagents
        if subagent_tool_calls:
            lines.append(f"\n{'─'*80}")
            lines.append(f"Internal Subagent Tool Calls: {len(subagent_tool_calls)}")
            lines.append(f"{'─'*80}")

            # Group by subagent
            by_subagent = {}
            for call in subagent_tool_calls:
                subagent = call.get("subagent", "unknown")
                if subagent not in by_subagent:
                    by_subagent[subagent] = []
                by_subagent[subagent].append(call)

            for subagent, calls in by_subagent.items():
                lines.append(f"\n{subagent}:")

                # Count tools used
                tool_counts = {}
                for call in calls:
                    tool_name = call.get("data", {}).get("tool_name", "unknown")
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

                for tool_name, count in sorted(tool_counts.items()):
                    lines.append(f"  - {tool_name}: {count}x")

        if subagent_results:
            lines.append(f"\n{'─'*80}")
            lines.append(f"Subagent Results: {len(subagent_results)}")
            lines.append(f"{'─'*80}")

            for result in subagent_results:
                data = result.get("data", {})
                subagent_type = data.get("subagent_type", "unknown")
                result_len = data.get("result_length", 0)
                tool_use_id = data.get("tool_use_id", "unknown")

                lines.append(f"\n  - {subagent_type}")
                lines.append(f"    Tool Use ID: {tool_use_id}")
                lines.append(f"    Result Length: {result_len:,} chars")

        # Show text output from subagents
        if subagent_text_blocks:
            lines.append(f"\n{'─'*80}")
            lines.append(f"Subagent Text Output: {len(subagent_text_blocks)} complete text blocks captured")
            lines.append(f"{'─'*80}")

            # Group by subagent
            by_subagent = {}
            total_chars = 0
            for text_block in subagent_text_blocks:
                subagent = text_block.get("subagent", "unknown")
                text_len = text_block.get("data", {}).get("text_length", 0)
                total_chars += text_len

                if subagent not in by_subagent:
                    by_subagent[subagent] = {"blocks": 0, "chars": 0}
                by_subagent[subagent]["blocks"] += 1
                by_subagent[subagent]["chars"] += text_len

            for subagent, stats in sorted(by_subagent.items()):
                lines.append(f"  {subagent}: {stats['blocks']} text blocks ({stats['chars']:,} chars)")

            lines.append(f"\n  Total text output: {total_chars:,} characters")

            # Show preview of first few text blocks
            lines.append(f"\n  Preview of text blocks:")
            for i, text_block in enumerate(subagent_text_blocks[:3]):
                subagent = text_block.get("subagent", "unknown")
                text = text_block.get("data", {}).get("text", "")
                preview = text[:200] + "..." if len(text) > 200 else text
                lines.append(f"\n    [{subagent}]:")
                lines.append(f"    {preview}")

        # Success note
        if subagent_tool_calls or subagent_text_blocks:
            lines.append(f"\n{'─'*80}")
            lines.append("✓ Subagent internal messages captured successfully!")
            lines.append("  Using StreamEvent with parent_tool_use_id tracking")
            if subagent_tool_calls:
                lines.append(f"  - Tool calls: {len(subagent_tool_calls)}")
            if subagent_text_blocks:
                lines.append(f"  - Complete text blocks: {len(subagent_text_blocks)}")
            lines.append(f"{'─'*80}")

        # Extract tool calls
        tool_calls = [e for e in events if e.get("event_type") == "tool_call"]
        if tool_calls:
            lines.append(f"\nTotal Tool Calls: {len(tool_calls)}")
            tools_used = {}
            for tc in tool_calls:
                tool_name = tc.get("data", {}).get("tool_name", "unknown")
                tools_used[tool_name] = tools_used.get(tool_name, 0) + 1

            lines.append("Tools Used:")
            for tool, count in sorted(tools_used.items()):
                lines.append(f"  {tool}: {count}")

        # Cost summary
        results = [e for e in events if e.get("event_type") == "final_result"]
        if results:
            last_result = results[-1]
            usage = last_result.get("data", {}).get("usage", {})
            if usage:
                lines.append("\nCost Summary:")
                lines.append(f"  Input tokens: {usage.get('input_tokens', 0):,}")
                lines.append(f"  Output tokens: {usage.get('output_tokens', 0):,}")
                lines.append(f"  Cache write: {usage.get('cache_write', 0):,}")
                lines.append(f"  Cache read: {usage.get('cache_read', 0):,}")
                lines.append(f"  Total cost: ${usage.get('total_cost_usd', 0):.4f}")

        lines.append("\n" + "=" * 80)
        lines.append(f"Full logs: {self.session_file}")
        lines.append("=" * 80)

        return "\n".join(lines)
