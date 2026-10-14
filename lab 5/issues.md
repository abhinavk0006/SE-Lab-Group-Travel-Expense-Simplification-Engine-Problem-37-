# Static analysis issue log

Line numbers below refer to the original `todo_manager.py` on the repository's `main` branch.

| Issue | Type / severity | Line(s) | Description | Fix approach |
|---|---|---:|---|---|
| Unsafe deserialization | Security / high | 44-46 | `pickle.load` can execute code from a malicious or tampered task file. | Replaced pickle persistence with JSON parsing and UTF-8 text files. |
| Shell command injection | Security / high | 55-57 | `os.system` concatenates an address into a shell command, allowing shell metacharacters to alter the command. | Removed the unused email helper; the demo does not need to invoke a system mail program. |
| Mutable default argument | Bug / medium | 11-13 | The default `labels=[]` is shared between calls, so labels can leak between tasks. | Use `None`, then create a fresh list for every call. |
| Unused argument / missing stored labels | Quality / low | 11-14 | `labels` was mutated but not saved to the task, and its default accumulated state. | Copy and store labels in each task record, then add priority without mutating the caller's list. |
| Missing task lookup result | Quality / low | 29-33 | `findTask` implicitly returned `None`, while the demo comment notes the miss is silent. | Return `None` explicitly and keep the demo output clear. |
| Unsafe empty random selection | Bug / medium | 74 | `random.choice` raises `IndexError` when no tasks remain pending. | Check for an empty pending list before selecting a suggestion. |
| PEP 8 and naming violations | Style / low | throughout | CamelCase function names and inconsistent spacing/line breaks violate common style rules. | Rename functions to snake_case and format consistently. |
| Import/use mismatch | Quality / low | 1-5 | `os` was only used by the unsafe mail helper; the source included several operations with no validation. | Removed unused `os`; validate priorities before storing them. |

## Verification note

The Python runtime is available, but Pylint, Bandit, and Flake8 are not installed in this environment. The reports required by the handout have therefore not been generated, and tool scores are not claimed. Run the three commands in the repository README after installing the tools to produce authoritative before/after reports.
