#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Build script for TypstBlog
Converts .typ files to HTML and PDF, injects metadata
Reads post configuration from posts.yaml
"""

import json
import re
import shutil
import subprocess
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DIST_DIR = SCRIPT_DIR / "dist"
POSTS_DIR = DIST_DIR / "posts"
POSTS_YAML = SCRIPT_DIR / "posts.yaml"

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

def load_posts_yaml():
    """Load and parse posts.yaml configuration"""
    if not POSTS_YAML.exists():
        print(f"⚠️  {POSTS_YAML} not found!")
        print("Create a posts.yaml file with your post configuration")
        sys.exit(1)

    with open(POSTS_YAML, 'r') as f:
        config = yaml.safe_load(f)

    if not config or 'posts' not in config:
        print("⚠️  posts.yaml must contain a 'posts' list")
        sys.exit(1)

    return config

def create_page_template(title, content, post_slug, commit, post_list):
    """Wrap post content in a complete HTML page"""
    # Generate navigation items
    nav_items = ""
    for post in post_list:
        active_class = ' class="active"' if post['slug'] == post_slug else ''
        nav_items += f'''
                <div class="post-item"{active_class}>
                    <a href="{post['html']}">{post['title']}</a>
                    <a href="{post['pdf']}" class="pdf-link" title="Download PDF">📄</a>
                    <div class="post-meta">{datetime.fromisoformat(post['modified']).strftime('%B %d, %Y')}</div>
                </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - TypstBlog</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header>
        <h1><a href="../index.html">TypstBlog</a></h1>
        <p class="tagline">A statically-generated blog with email comments</p>
    </header>

    <div class="container">
        <nav id="post-list">
            <h2>Posts</h2>
            <div id="nav-posts">{nav_items}
            </div>
        </nav>

        <main id="content">
            {content}
        </main>
    </div>

    <footer>
        <p>Built with Typst | <a href="https://github.com">Source</a></p>
    </footer>

    <script src="../js/comments.js"></script>
    <script>
        // Initialize comments on page load
        document.addEventListener('DOMContentLoaded', () => {{
            initComments('{post_slug}', '{commit}');
        }});
    </script>
</body>
</html>'''

def build_post(post_config):
    """Build a single post from YAML configuration"""
    slug = post_config['slug']
    title = post_config['title']
    source_path = Path(post_config['source'])
    main_file = post_config['main_file']
    post_format = post_config.get('format', 'typst')
    post_date = post_config.get('date')

    print(f"\n📄 Building {slug}...")

    # Resolve source path (handle relative paths from script dir)
    if not source_path.is_absolute():
        source_path = (SCRIPT_DIR / source_path).resolve()

    if not source_path.exists():
        print(f"  ✗ Source path not found: {source_path}")
        return None

    # Find the main file
    main_file_path = source_path / main_file
    if not main_file_path.exists():
        print(f"  ✗ Main file not found: {main_file_path}")
        return None

    # Create output paths
    html_fragment = POSTS_DIR / f"{slug}_fragment.html"
    html_out = POSTS_DIR / f"{slug}.html"
    pdf_out = POSTS_DIR / f"{slug}.pdf"

    # Build based on format
    if post_format == 'typst':
        # Build HTML fragment
        if not run_command(
            f"typst compile --features html '{main_file_path}' '{html_fragment}' --format html",
            f"Compiling {slug} → HTML"
        ):
            return None

        # Build PDF
        if not run_command(
            f"typst compile '{main_file_path}' '{pdf_out}'",
            f"Compiling {slug} → PDF"
        ):
            return None
    else:
        print(f"  ✗ Unsupported format: {post_format}")
        return None

    # Get git commit hash
    commit = get_git_commit()

    # Read the fragment content
    fragment_content = html_fragment.read_text()

    # Extract just the body content (remove the wrapping html/head/body tags)
    body_match = re.search(r'<body>(.*)</body>', fragment_content, re.DOTALL)
    if body_match:
        fragment_content = body_match.group(1)

    fragment_content = fragment_content.replace("{{COMMIT}}", commit)

    # Use date from YAML or file modification time
    if post_date:
        if isinstance(post_date, str):
            modified = datetime.fromisoformat(post_date).isoformat()
        else:
            modified = datetime.combine(post_date, datetime.min.time()).isoformat()
    else:
        mtime = main_file_path.stat().st_mtime
        modified = datetime.fromtimestamp(mtime).isoformat()

    post_meta = {
        "slug": slug,
        "title": title,
        "html": f"posts/{slug}.html",
        "pdf": f"posts/{slug}.pdf",
        "modified": modified,
        "commit": commit,
        "content": fragment_content
    }

    return post_meta

def generate_manifest(posts):
    """Generate a JSON manifest of all posts"""
    # Clean up posts for manifest (remove content field)
    manifest_posts = [{k: v for k, v in p.items() if k != 'content'} for p in posts]
    manifest_path = DIST_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_posts, indent=2))
    print(f"\n✓ Generated manifest with {len(posts)} posts")

def generate_index(posts):
    """Generate the index.html with post list"""
    # Generate navigation items
    nav_items = ""
    for post in posts:
        nav_items += f'''
                <div class="post-item">
                    <a href="{post['html']}">{post['title']}</a>
                    <a href="{post['pdf']}" class="pdf-link" title="Download PDF">📄</a>
                    <div class="post-meta">{datetime.fromisoformat(post['modified']).strftime('%B %d, %Y')}</div>
                </div>'''

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TypstBlog - Email-Commentable Blog</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>TypstBlog</h1>
        <p class="tagline">A statically-generated blog with email comments</p>
    </header>

    <div class="container">
        <nav id="post-list">
            <h2>Posts</h2>
            <div id="nav-posts">{nav_items}
            </div>
        </nav>

        <main id="content">
            <div class="welcome">
                <h2>Welcome!</h2>
                <p>This is a blog built with Typst and a sprinkle of JavaScript.</p>
                <p>Select a post from the sidebar to get started.</p>
                <h3>Features:</h3>
                <ul>
                    <li>📝 Posts written in <a href="https://typst.app" target="_blank">Typst</a></li>
                    <li>📄 PDF fallbacks for each post</li>
                    <li>💬 Email-based commenting (hover over paragraphs!)</li>
                    <li>🚀 No backend required - fully static</li>
                </ul>
            </div>
        </main>
    </div>

    <footer>
        <p>Built with Typst | <a href="https://github.com">Source</a></p>
    </footer>
</body>
</html>'''

    index_path = DIST_DIR / "index.html"
    index_path.write_text(index_html)
    print(f"✓ Generated index.html")

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

    # Load posts configuration
    config = load_posts_yaml()
    post_configs = config['posts']

    if not post_configs:
        print("⚠️  No posts defined in posts.yaml")
        sys.exit(1)

    print(f"Found {len(post_configs)} post(s) in posts.yaml\n")

    # Ensure directories exist
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    # Build each post (this generates fragments and metadata)
    posts = []
    for post_config in post_configs:
        post_meta = build_post(post_config)
        if post_meta:
            posts.append(post_meta)

    if not posts:
        print("⚠️  No posts were successfully built")
        sys.exit(1)

    # Now generate complete HTML pages for each post
    print("\n📝 Generating complete HTML pages...")
    for post in posts:
        complete_html = create_page_template(
            title=post['title'],
            content=post['content'],
            post_slug=post['slug'],
            commit=post['commit'],
            post_list=posts
        )
        html_path = POSTS_DIR / f"{post['slug']}.html"
        html_path.write_text(complete_html)
        print(f"  ✓ {post['slug']}.html")

        # Clean up fragment file
        fragment_path = POSTS_DIR / f"{post['slug']}_fragment.html"
        if fragment_path.exists():
            fragment_path.unlink()

    # Generate manifest
    generate_manifest(posts)

    # Generate index page
    generate_index(posts)

    print(f"\n✅ Build complete! {len(posts)} post(s) built")
    print(f"   Output: {DIST_DIR.absolute()}")

if __name__ == "__main__":
    main()
