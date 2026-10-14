# Before and after

| Area | Before | After |
|---|---|---|
| Persistence | `pickle.load` reads executable serialized data. | JSON is used for task storage and loading. |
| Email helper | `os.system` builds a shell command with an address. | Unused shell-based helper removed. |
| Labels | Mutable `labels=[]` default was mutated and not stored. | `None` default; each task gets its own stored label list. |
| Task IDs | `len(tasks) + 1` can reuse an ID after deletions. | ID is one greater than the largest existing key. |
| Priority | Unknown priorities could fail later during sorting. | Priority is validated when adding a task. |
| Empty pending list | `random.choice` could raise `IndexError`. | Empty list is handled before suggesting a task. |
| Style / entry point | Mixed naming, formatting, and unconditional `main()` call. | snake_case names, consistent formatting, and main guard. |
| Static analyzer reports | Not yet captured in this environment. | Not yet captured: Pylint, Bandit, and Flake8 are unavailable; PyPI could not be reached to install them. |

## Scope

Before source is the repository's original `main` version. After source is the revised local version. No commits or pushes were made to GitHub.
