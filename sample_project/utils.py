"""
Utility functions for TaskFlow.
"""

from datetime import datetime
from typing import Optional


def format_date(date_str: Optional[str]) -> Optional[str]:
    """Format a date string for display."""
    if not date_str:
        return None
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def priority_color(priority: str) -> str:
    """Get ANSI color code for priority level."""
    colors = {
        "high": "\033[91m",    # Red
        "medium": "\033[93m",  # Yellow
        "low": "\033[92m",     # Green
    }
    return colors.get(priority, "")


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def is_overdue(due_date: Optional[str]) -> bool:
    """Check if a task is overdue."""
    if not due_date:
        return False
    try:
        due = datetime.fromisoformat(due_date)
        return due.date() < datetime.now().date()
    except ValueError:
        return False
