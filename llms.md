# Use UV for scripts

At the top of a file, ensure the shebang and dependencies are listed in the file.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyyaml",
#     "markdown",
# ]
# ///
```

After `chmod` - run the script without calling `uv` or `python` like `./my_script.py`

# Testing after `./build.py`

```bash
uv run python -m http.server 8000 --directory docs
```