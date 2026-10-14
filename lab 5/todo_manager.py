"""Manage a small in-memory to-do list and demonstrate JSON persistence."""

import json
import random
from datetime import datetime
from pathlib import Path


tasks = {}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def add_task(title, priority="medium", labels=None):
    """Add a task and return its numeric ID."""
    if priority not in PRIORITY_ORDER:
        raise ValueError(f"Unsupported priority: {priority}")
    task_id = max(tasks, default=0) + 1
    task_labels = list(labels) if labels is not None else []
    if priority not in task_labels:
        task_labels.append(priority)
    tasks[task_id] = {
        "title": title,
        "priority": priority,
        "labels": task_labels,
        "done": False,
        "created": datetime.now().isoformat(),
    }
    return task_id


def complete_task(task_id):
    """Mark a task complete, returning whether its ID exists."""
    if task_id not in tasks:
        print("No task with id", task_id)
        return False
    tasks[task_id]["done"] = True
    return True


def pending_tasks():
    """Return pending task titles ordered by priority."""
    pending = [task for task in tasks.values() if not task["done"]]
    pending.sort(key=lambda task: PRIORITY_ORDER[task["priority"]])
    return [task["title"] for task in pending]


def find_task(keyword):
    """Return the ID of the first matching task, or None."""
    normalized_keyword = keyword.casefold()
    for task_id, task in tasks.items():
        if normalized_keyword in task["title"].casefold():
            return task_id
    return None


def save_tasks(file_name="tasks.json"):
    """Save tasks as JSON so loading cannot execute serialized code."""
    path = Path(file_name)
    serializable_tasks = {str(task_id): task for task_id, task in tasks.items()}
    path.write_text(json.dumps(serializable_tasks, indent=2), encoding="utf-8")


def load_tasks(file_name="tasks.json"):
    """Load task data from JSON and return it with integer IDs."""
    path = Path(file_name)
    loaded_data = json.loads(path.read_text(encoding="utf-8"))
    return {int(task_id): task for task_id, task in loaded_data.items()}


def export_json(file_name="tasks_export.json"):
    """Export the current tasks as a JSON object."""
    path = Path(file_name)
    serializable_tasks = {str(task_id): task for task_id, task in tasks.items()}
    path.write_text(json.dumps(serializable_tasks, indent=2), encoding="utf-8")


def main():
    """Run a short demonstration of the task manager."""
    add_task("Submit lab report", "high")
    add_task("Buy groceries")
    add_task("Call plumber", "low")
    add_task("Book train tickets", "high")
    complete_task(2)
    complete_task(99)
    print("Pending tasks:", pending_tasks())
    print("Task id for 'plumber':", find_task("plumber"))
    print("Task id for 'gym':", find_task("gym"))
    pending = pending_tasks()
    if pending:
        print("Try this next:", random.choice(pending))
    else:
        print("No pending tasks to suggest.")
    save_tasks()
    restored = load_tasks()
    print("Tasks restored from file:", len(restored))
    export_json()
    print("Exported tasks to tasks_export.json")


if __name__ == "__main__":
    main()
