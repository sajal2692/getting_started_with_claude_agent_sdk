#!/usr/bin/env python3
"""
TaskFlow - A simple CLI task manager.

This is a sample project for the Claude Agent SDK course.
Students will analyze, modify, and extend this project using AI agents.
"""

import argparse
import sys
from datetime import datetime
from storage import TaskStorage
from utils import format_date, priority_color


def main():
    parser = argparse.ArgumentParser(
        description="TaskFlow - Manage your tasks from the command line"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add task
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-p", "--priority", choices=["low", "medium", "high"],
                           default="medium", help="Task priority")
    add_parser.add_argument("-d", "--due", help="Due date (YYYY-MM-DD)")

    # List tasks
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("-s", "--status", choices=["pending", "done", "all"],
                            default="all", help="Filter by status")

    # Complete task
    done_parser = subparsers.add_parser("done", help="Mark a task as complete")
    done_parser.add_argument("task_id", type=int, help="Task ID to mark complete")

    # Delete task
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="Task ID to delete")

    args = parser.parse_args()

    storage = TaskStorage()

    if args.command == "add":
        task = storage.add_task(
            title=args.title,
            priority=args.priority,
            due_date=args.due
        )
        print(f"Added task #{task['id']}: {task['title']}")

    elif args.command == "list":
        tasks = storage.get_tasks(status=args.status)
        if not tasks:
            print("No tasks found.")
            return

        print(f"\n{'ID':<4} {'Status':<8} {'Priority':<8} {'Due':<12} {'Title'}")
        print("-" * 60)
        for task in tasks:
            status = "done" if task["completed"] else "pending"
            due = format_date(task.get("due_date")) or "-"
            priority = task["priority"]
            print(f"{task['id']:<4} {status:<8} {priority:<8} {due:<12} {task['title']}")
        print()

    elif args.command == "done":
        if storage.complete_task(args.task_id):
            print(f"Task #{args.task_id} marked as complete!")
        else:
            print(f"Task #{args.task_id} not found.")
            sys.exit(1)

    elif args.command == "delete":
        if storage.delete_task(args.task_id):
            print(f"Task #{args.task_id} deleted.")
        else:
            print(f"Task #{args.task_id} not found.")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
