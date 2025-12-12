# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal blog/project repository called "Without Objective" - a collection of writings, experiments, and projects built on the philosophy of creating without rigid objectives. The primary purpose is hosting a static blog built with Python, Typst, and Markdown, deployed via GitHub Pages.

## Build System

The repository uses a custom Python-based static site generator with UV for dependency management.

Always write new python scripts with a `uv` block at the top. Change dependencies as needed.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmt",
#     "logfmter",
#     "rich",
# ]
# ///
```

When we need to run a command, write the instruction into a `justfile` and execute it instead of running the command directly. This allows us to capture a history of what commands are important / repeated.

## Development Philosophy

This repository follows a "Without Objective" philosophy:
- Projects are meant to be exploratory and disposable
- Prefer building and moving on over endless refinement
- Systems should be simple enough to abandon and rebuild
- Focus on creating rather than maintaining

When contributing or modifying:
- Don't over-engineer solutions
- Prefer simple, obvious implementations
- It's okay for projects to be incomplete or experimental
- Documentation is minimal and task-focused (no fluff)
- System Crashes are better than endless Try-Except blocks

## Technology Stack

- **Python 3.14+** with UV for scripting
- **Typst** for document compilation (optional, only for Typst posts)
- **Markdown** with Python markdown library for posts
- **Git** for version control and post history
- **GitHub Pages** for hosting (static site in `docs/`)
- **Rust** for Android experiments (cargo-apk, wgpu, egui, winit)
