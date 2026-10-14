# Reflection

*These concise answers use the lab's stated learning outcomes. The attached handout does not show a separate list of four reflection questions.*

1. **What is static analysis?** It checks source code without running it and flags likely bugs, security risks, and style issues.
2. **What did the tools contribute?** Pylint reviewed code quality, Flake8 checked style, and Bandit looked for risky security patterns.
3. **What did I fix?** I replaced unsafe pickle persistence, removed shell command construction, fixed shared mutable state, and guarded empty task selection.
4. **What are the limits?** Clean reports cannot prove a program is correct; findings need human review and runtime checks.
