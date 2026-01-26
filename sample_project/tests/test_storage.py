"""Tests for the storage module."""

import os
import pytest
from storage import TaskStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage instance."""
    filepath = tmp_path / "test_tasks.json"
    return TaskStorage(filepath=str(filepath))


class TestTaskStorage:
    """Tests for TaskStorage class."""

    def test_add_task(self, temp_storage):
        """Test adding a task."""
        task = temp_storage.add_task("Test task", priority="high")

        assert task["id"] == 1
        assert task["title"] == "Test task"
        assert task["priority"] == "high"
        assert task["completed"] is False

    def test_add_multiple_tasks(self, temp_storage):
        """Test adding multiple tasks."""
        task1 = temp_storage.add_task("First task")
        task2 = temp_storage.add_task("Second task")

        assert task1["id"] == 1
        assert task2["id"] == 2

    def test_get_tasks_all(self, temp_storage):
        """Test getting all tasks."""
        temp_storage.add_task("Task 1")
        temp_storage.add_task("Task 2")

        tasks = temp_storage.get_tasks(status="all")
        assert len(tasks) == 2

    def test_get_tasks_pending(self, temp_storage):
        """Test filtering pending tasks."""
        temp_storage.add_task("Task 1")
        task2 = temp_storage.add_task("Task 2")
        temp_storage.complete_task(task2["id"])

        pending = temp_storage.get_tasks(status="pending")
        assert len(pending) == 1
        assert pending[0]["title"] == "Task 1"

    def test_complete_task(self, temp_storage):
        """Test completing a task."""
        task = temp_storage.add_task("Test task")

        result = temp_storage.complete_task(task["id"])

        assert result is True
        assert temp_storage.get_task(task["id"])["completed"] is True

    def test_complete_nonexistent_task(self, temp_storage):
        """Test completing a task that doesn't exist."""
        result = temp_storage.complete_task(999)
        assert result is False

    def test_delete_task(self, temp_storage):
        """Test deleting a task."""
        task = temp_storage.add_task("Test task")

        result = temp_storage.delete_task(task["id"])

        assert result is True
        assert temp_storage.get_task(task["id"]) is None

    def test_delete_nonexistent_task(self, temp_storage):
        """Test deleting a task that doesn't exist."""
        result = temp_storage.delete_task(999)
        assert result is False
