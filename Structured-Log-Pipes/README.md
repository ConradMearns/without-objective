# Existing Features

- UNIX piping
- UNIX KISS
- Structured Logging

# Pains

UNIX style piping is cool but I haven't ever found it useful for writing 'enterprise' software.

It's good for a little bash script, but I could care less to learn Bash. 
Especially when I'm trying to make scalable, reactive systems.

# Needs

- Better methods for branching
- way to enable reactivity a the script scale

# Features

- JSONL stdout

## Progress

```bash
without-objective/Structured-Log-Pipes$ uv run python fibwait.py 
# {"a": 1, "b": 2}
without-objective/Structured-Log-Pipes$ uv run python fibwait.py | uv run python fibwait.py 
# {"a": 2, "b": 3}
without-objective/Structured-Log-Pipes$ uv run python fibwait.py | uv run python fibwait.py | uv run python fibwait.py
# {"a": 3, "b": 5}
without-objective/Structured-Log-Pipes$ 
```