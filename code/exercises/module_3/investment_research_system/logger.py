"""
Logging utilities for multi-agent system.

Handles parallel subagent logging with proper organization and timestamps.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import threading
from claude_agent_sdk import AssistantMessage, TextBlock
from claude_agent_sdk.types import StreamEvent


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
                input_tokens = getattr(usage, 'input_tokens', 0)
                output_tokens = getattr(usage, 'output_tokens', 0)
                cache_write = getattr(usage, 'cache_creation_input_tokens', 0)
                cache_read = getattr(usage, 'cache_read_input_tokens', 0)

                data["usage"] = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cache_write": cache_write,
                    "cache_read": cache_read
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

    def show_progress_indicators(self, message, progress_state: dict):
        """Show progress indicators in console (regardless of debug mode).

        Args:
            message: Message to check for progress indicators
            progress_state: Mutable dict with keys: subagents_spawned, synthesis_started, dashboard_started
        """
        if not isinstance(message, AssistantMessage):
            return

        # Detect Task tool calls (subagent spawning)
        for block in message.content:
            if hasattr(block, 'name') and block.name == "Task":
                if hasattr(block, 'input') and isinstance(block.input, dict):
                    subagent_type = block.input.get('subagent_type', 'unknown')

                    # Only show each subagent spawn once
                    if subagent_type not in progress_state["subagents_spawned"]:
                        progress_state["subagents_spawned"].add(subagent_type)

                        # Friendly names for subagents
                        friendly_names = {
                            "news-sentiment": "News & Sentiment Analyst",
                            "fundamental-analysis": "Fundamental Analyst",
                            "competitive-analysis": "Competitive Analyst",
                            "dashboard-builder": "Dashboard Builder"
                        }

                        name = friendly_names.get(subagent_type, subagent_type)
                        print(f"\n>> Spawning: {name}")

        # Detect completion and synthesis in text blocks
        for block in message.content:
            if isinstance(block, TextBlock):
                text = block.text.lower()

                # Detect when research is complete and synthesis starts
                if ("all three research" in text or
                    "research teams have completed" in text or
                    "all three analyst" in text or
                    "research subagents completed" in text or
                    "analysis teams have completed" in text):

                    if not progress_state["synthesis_started"]:
                        progress_state["synthesis_started"] = True
                        print(f"\n>> All research subagents completed")
                        print(f">> Coordinator synthesizing findings...")

                # Detect when dashboard building starts
                if ("dashboard" in text and "builder" in text and
                    not progress_state["dashboard_started"] and
                    progress_state["synthesis_started"]):

                    progress_state["dashboard_started"] = True
                    print(f"\n>> Starting dashboard visualization...")

    def log_stream_event(self, stream_event: StreamEvent, progress_state: dict):
        """Log streaming events from subagents - accumulate and log complete text blocks.

        Args:
            stream_event: StreamEvent containing event and parent_tool_use_id
            progress_state: Mutable dict with keys: active_tasks, text_accumulator
        """
        parent_tool_id = stream_event.parent_tool_use_id
        event = stream_event.event
        event_type = event.get("type", "unknown")

        # Determine which subagent this belongs to
        subagent_name = "coordinator"
        if parent_tool_id and parent_tool_id in progress_state["active_tasks"]:
            subagent_name = progress_state["active_tasks"][parent_tool_id]

        # Log different event types
        if event_type == "content_block_start":
            block = event.get("content_block", {})
            block_type = block.get("type", "unknown")
            block_index = event.get("index", -1)

            if block_type == "tool_use":
                # Subagent is calling a tool
                tool_name = block.get("name", "unknown")
                tool_id = block.get("id", "unknown")

                self.log_event(
                    "subagent_tool_call",
                    {
                        "tool_name": tool_name,
                        "tool_id": tool_id,
                        "from_subagent": parent_tool_id is not None,
                        "parent_tool_id": parent_tool_id
                    },
                    subagent=subagent_name
                )
            elif block_type == "text":
                # Initialize text accumulator for this block
                block_key = (parent_tool_id, block_index)
                progress_state["text_accumulator"][block_key] = ""

        elif event_type == "content_block_delta":
            # Accumulate text deltas into the text block
            delta = event.get("delta", {})
            delta_type = delta.get("type", "unknown")
            block_index = event.get("index", -1)

            if delta_type == "text_delta":
                text = delta.get("text", "")
                block_key = (parent_tool_id, block_index)

                # Accumulate text for this block
                if block_key in progress_state["text_accumulator"]:
                    progress_state["text_accumulator"][block_key] += text
                else:
                    # Initialize if not already started
                    progress_state["text_accumulator"][block_key] = text

        elif event_type == "content_block_stop":
            # Log the complete text block now that it's finished
            block_index = event.get("index", -1)
            block_key = (parent_tool_id, block_index)

            if block_key in progress_state["text_accumulator"]:
                complete_text = progress_state["text_accumulator"][block_key]

                # Log the complete text block
                self.log_event(
                    "subagent_text_complete",
                    {
                        "text": complete_text,
                        "text_length": len(complete_text),
                        "block_index": block_index,
                        "from_subagent": parent_tool_id is not None,
                        "parent_tool_id": parent_tool_id
                    },
                    subagent=subagent_name
                )

                # Clean up accumulator
                del progress_state["text_accumulator"][block_key]

        elif event_type == "message_start":
            # Log when a message starts (from subagent or coordinator)
            message = event.get("message", {})
            self.log_event(
                "message_start",
                {
                    "role": message.get("role", "unknown"),
                    "from_subagent": parent_tool_id is not None,
                    "parent_tool_id": parent_tool_id
                },
                subagent=subagent_name
            )

    def identify_and_log_subagents(self, message, progress_state: dict):
        """Identify subagent activity and log appropriately.

        Args:
            message: Message to analyze for subagent activity
            progress_state: Mutable dict with key: active_tasks
        """
        # Determine which subagent this message belongs to
        subagent_name = "coordinator"

        # Check if message has parent_tool_use_id (from subagent execution)
        if hasattr(message, 'parent_tool_use_id') and message.parent_tool_use_id:
            parent_tool_id = message.parent_tool_use_id
            if parent_tool_id in progress_state["active_tasks"]:
                subagent_name = progress_state["active_tasks"][parent_tool_id]

        # Handle AssistantMessage - contains tool use requests
        if isinstance(message, AssistantMessage):
            task_calls = {}  # Map tool_id to subagent_type

            for block in message.content:
                # Track Task tool calls (subagent spawning)
                if hasattr(block, 'name') and block.name == "Task":
                    if hasattr(block, 'input') and isinstance(block.input, dict):
                        subagent_type = block.input.get('subagent_type')
                        tool_id = getattr(block, 'id', None)
                        prompt = block.input.get('prompt', '')[:200]

                        if subagent_type and tool_id:
                            task_calls[tool_id] = subagent_type
                            progress_state["active_tasks"][tool_id] = subagent_type

                            # Log spawn with task details
                            self.log_event(
                                "subagent_spawn",
                                {
                                    "subagent_type": subagent_type,
                                    "tool_id": tool_id,
                                    "prompt_preview": prompt
                                },
                                subagent="coordinator"
                            )

            # Log the full assistant message with correct subagent attribution
            self.log_message(message, subagent=subagent_name)

        # Handle other message types - check for tool results
        else:
            # Determine subagent from parent_tool_use_id
            subagent_name = "coordinator"
            if hasattr(message, 'parent_tool_use_id') and message.parent_tool_use_id:
                parent_tool_id = message.parent_tool_use_id
                if parent_tool_id in progress_state["active_tasks"]:
                    subagent_name = progress_state["active_tasks"][parent_tool_id]

            # Check if this message contains tool results
            if hasattr(message, 'content'):
                for block in message.content:
                    # Look for ToolResultBlock from Task tool
                    if hasattr(block, 'tool_use_id') and hasattr(block, 'content'):
                        tool_use_id = block.tool_use_id

                        # Check if this is a result from a subagent Task
                        if tool_use_id in progress_state["active_tasks"]:
                            subagent_type = progress_state["active_tasks"][tool_use_id]
                            result_content = str(block.content)

                            # Log as subagent result
                            self.log_event(
                                "subagent_result",
                                {
                                    "subagent_type": subagent_type,
                                    "tool_use_id": tool_use_id,
                                    "result": result_content[:1000],
                                    "result_length": len(result_content)
                                },
                                subagent=subagent_type
                            )

                            # Clean up completed task
                            del progress_state["active_tasks"][tool_use_id]

            # Log the full message with correct subagent attribution
            self.log_message(message, subagent=subagent_name)

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


        lines.append("\n" + "=" * 80)
        lines.append(f"Full logs: {self.session_file}")
        lines.append("=" * 80)

        return "\n".join(lines)
