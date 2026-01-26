# TaskFlow

A simple CLI task manager for managing your daily tasks.

## Features

- Add tasks with priority levels (low, medium, high)
- Set due dates for tasks
- List tasks filtered by status
- Mark tasks as complete
- Delete tasks

## Usage

```bash
# Add a task
python task_manager.py add "Buy groceries" -p high -d 2024-03-20

# List all tasks
python task_manager.py list

# List only pending tasks
python task_manager.py list -s pending

# Mark a task as done
python task_manager.py done 1

# Delete a task
python task_manager.py delete 1
```

## Project Structure

```
taskflow/
├── task_manager.py   # Main CLI entry point
├── storage.py        # Task persistence layer
├── utils.py          # Utility functions
├── tests/            # Test suite
│   ├── test_storage.py
│   └── test_utils.py
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## Running Tests

```bash
pytest tests/
```
