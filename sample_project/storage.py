"""
Storage module for TaskFlow.

Handles persistence of tasks to a JSON file.
"""

import json
import os
from datetime import datetime
from typing import Optional


class TaskStorage:
    """Manages task storage using a JSON file."""

    def __init__(self, filepath: str = "tasks.json"):
        self.filepath = filepath
        self.tasks = self._load()

    def _load(self) -> list:
        """Load tasks from file."""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return json.load(f)
        return []

    def _save(self) -> None:
        """Save tasks to file."""
        with open(self.filepath, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def _next_id(self) -> int:
        """Get the next available task ID."""
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1

    def add_task(
        self,
        title: str,
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> dict:
        """Add a new task."""
        task = {
            "id": self._next_id(),
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self._save()
        return task

    def get_tasks(self, status: str = "all") -> list:
        """Get tasks filtered by status."""
        if status == "all":
            return self.tasks
        elif status == "pending":
            return [t for t in self.tasks if not t["completed"]]
        elif status == "done":
            return [t for t in self.tasks if t["completed"]]
        return self.tasks

    def get_task(self, task_id: int) -> Optional[dict]:
        """Get a single task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as complete."""
        task = self.get_task(task_id)
        if task:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            self._save()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                self.tasks.pop(i)
                self._save()
                return True
        return False
