#!/usr/bin/env -S uv run --script
"""
Build script for TypstBlog
Converts .typ files to HTML and PDF, injects metadata
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
SRC_DIR = Path("src")
DIST_DIR = Path("dist")
POSTS_DIR = DIST_DIR / "posts"

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"→ {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Failed: {result.stderr}")
        return False
    print(f"  ✓ Success")
    return True

def get_git_commit():
    """Get current git commit hash"""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"

def build_post(typ_file):
    """Build a single post: HTML and PDF"""
    stem = typ_file.stem
    html_out = POSTS_DIR / f"{stem}.html"
    pdf_out = POSTS_DIR / f"{stem}.pdf"

    print(f"\n📄 Building {stem}...")

    # Build HTML
    if not run_command(
        f"typst compile --features html '{typ_file}' '{html_out}' --format html",
        f"Compiling {stem} → HTML"
    ):
        return None

    # Build PDF
    if not run_command(
        f"typst compile '{typ_file}' '{pdf_out}'",
        f"Compiling {stem} → PDF"
    ):
        return None

    # Inject git commit hash into HTML
    commit = get_git_commit()
    html_content = html_out.read_text()
    html_content = html_content.replace("{{COMMIT}}", commit)
    html_out.write_text(html_content)

    # Get file modification time for sorting
    mtime = typ_file.stat().st_mtime

    return {
        "slug": stem,
        "title": stem.replace("-", " ").title(),
        "html": f"posts/{stem}.html",
        "pdf": f"posts/{stem}.pdf",
        "modified": datetime.fromtimestamp(mtime).isoformat(),
        "commit": commit
    }

def generate_manifest(posts):
    """Generate a JSON manifest of all posts"""
    manifest_path = DIST_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(posts, indent=2))
    print(f"\n✓ Generated manifest with {len(posts)} posts")

def check_typst():
    """Check if typst is installed"""
    result = subprocess.run(
        ["typst", "--version"],
        capture_output=True
    )
    if result.returncode != 0:
        print("⚠️  Typst not found!")
        print("Install it with: curl -fsSL https://typst.app/install.sh | sh")
        print("Or visit: https://github.com/typst/typst")
        sys.exit(1)

def main():
    print("🏗️  TypstBlog Builder\n")

    # Check dependencies
    check_typst()

    # Ensure directories exist
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all .typ files
    typ_files = list(SRC_DIR.glob("*.typ"))
    if not typ_files:
        print("⚠️  No .typ files found in src/")
        sys.exit(1)

    print(f"Found {len(typ_files)} post(s)\n")

    # Build each post
    posts = []
    for typ_file in typ_files:
        post_meta = build_post(typ_file)
        if post_meta:
            posts.append(post_meta)

    # Sort by modification time (newest first)
    posts.sort(key=lambda p: p['modified'], reverse=True)

    # Generate manifest
    generate_manifest(posts)

    print(f"\n✅ Build complete! {len(posts)} post(s) built")
    print(f"   Output: {DIST_DIR.absolute()}")

if __name__ == "__main__":
    main()
