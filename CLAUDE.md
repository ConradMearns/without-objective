# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal blog/project repository called "Without Objective" - a collection of writings, experiments, and projects built on the philosophy of creating without rigid objectives. The primary purpose is hosting a static blog built with Python, Typst, and Markdown, deployed via GitHub Pages.

## Build System

The repository uses a custom Python-based static site generator with UV for dependency management.

### Building the Blog

```bash
# Build all posts and generate the site
./build.py

# The script uses UV's inline dependency declaration
# UV will automatically handle dependencies (pyyaml, markdown)
```

The build process:
1. Reads `posts.yaml` for post configurations
2. Compiles Typst files to HTML/PDF or converts Markdown to HTML
3. Generates `docs/` directory with static site
4. Creates `manifest.json` for client-side navigation
5. Copies static assets (CSS, JS, fonts) from `static/` to `docs/`

### Collecting Post History

```bash
# Generate git commit history for posts
./collect_post_history.py

# Outputs to post_history.yaml
```

## Project Structure

### Core Build Files
- `build.py` - Main build script for the blog
- `collect_post_history.py` - Extracts git history for posts
- `posts.yaml` - Post configuration and site metadata
- `post_history.yaml` - Generated commit history

### Content Organization
- Root `.md` files - Individual blog posts written in Markdown
- `2025-04-08-Parsing-LLM-Output-Streams/` - Post with supporting files
- `Structured-Log-Pipes/` - Experiment with structured logging and UNIX philosophy
- `hello-rust-apk/` - Rust Android APK experiment

### Output
- `docs/` - Generated static site for GitHub Pages
  - `docs/posts/` - Compiled post HTML and PDFs
  - `docs/manifest.json` - Site metadata and post index
  - `docs/css/`, `docs/js/`, `docs/fonts/` - Static assets

### Static Assets
- `static/css/style.css` - Site styling
- `static/js/nav.js` - Client-side navigation
- `static/js/comments.js` - Email-based commenting system
- `static/fonts/` - Custom fonts (Departure Mono)

### Templates
- `templates/` - HTML templates (currently unused, system generates HTML in build.py)

## Blog Architecture

The blog uses a **hybrid approach**:
1. Python build script generates post HTML from source (Typst/Markdown)
2. Static HTML pages load navigation dynamically via JavaScript from `manifest.json`
3. No backend required - fully static, GitHub Pages compatible

### Post Configuration (posts.yaml)

Each post entry requires:
```yaml
posts:
  - slug: post-slug            # URL-safe identifier
    title: "Post Title"        # Display title
    source: ./path/to/source   # Source directory
    main_file: post.md         # Main post file
    format: markdown           # 'markdown' or 'typst'
    date: 2025-03-25          # Publication date

config:
  author: "Author Name"
  email: "email@example.com"
  site_title: "Site Title"
  tagline: "Site tagline"
```

### Post Formats

**Markdown posts**: Use standard markdown, compiled with Python `markdown` library (extensions: extra, codehilite)

**Typst posts**: Compiled with `typst` CLI to both HTML and PDF
- Requires `typst` installed: `curl -fsSL https://typst.app/install.sh | sh`

## Subproject: Structured-Log-Pipes

An experiment in "effectual event sourcing" - using structured logging (JSONL/logfmt) to pipe data between scripts following UNIX philosophy.

### Key Scripts
- `scan_partition.py` - Discovers files in a directory
- `stat_partition.py` - Collects file metadata
- `hash_items.py` - Computes file hashes
- `analyze_data.py` - Analyzes collected data
- `slap.py` - Shared logging utilities

All scripts use UV's inline dependency declaration and can be piped together:
```bash
./scan_partition.py | ./stat_partition.py | ./hash_items.py
# Or analyze saved logs
./analyze_data.py
```

## Subproject: hello-rust-apk

Rust Android APK development experiment using cargo-apk, winit, wgpu, and egui.

### Building the Android APK

**Prerequisites**:
- Java 17+ (`openjdk-17-jdk`)
- Android NDK (r26d)
- Android SDK with build-tools 34.0.0
- Rust with `aarch64-linux-android` target
- `cargo-apk` installed

**Build**:
```bash
cd hello-rust-apk/hello_android
cargo apk build              # Debug APK
cargo apk build --release    # Release APK
```

APK output: `target/debug/apk/hello_android.apk` or `target/release/apk/hello_android.apk`

See `hello-rust-apk/README.md` for full setup instructions.

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

## Technology Stack

- **Python 3.14+** with UV for scripting
- **Typst** for document compilation (optional, only for Typst posts)
- **Markdown** with Python markdown library for posts
- **Git** for version control and post history
- **GitHub Pages** for hosting (static site in `docs/`)
- **Rust** for Android experiments (cargo-apk, wgpu, egui, winit)

## Git Workflow

The repository is on branch `main`. When creating posts or making changes:
1. Edit source files (Markdown/Typst in root or subdirectories)
2. Update `posts.yaml` if adding new posts
3. Run `./build.py` to regenerate the site
4. Commit both source and generated `docs/` directory
5. GitHub Pages serves from `docs/` on main branch
