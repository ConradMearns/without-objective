#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyyaml",
#     "markdown",
# ]
# ///
"""
Build script for TypstBlog
Converts .typ files and .md files to HTML and PDF, injects metadata
Reads post configuration from posts.yaml
Outputs to docs/ directory for GitHub Pages compatibility
"""

import json
import re
import shutil
import subprocess
import sys
import yaml
import markdown
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR / "docs"
POSTS_DIR = DOCS_DIR / "posts"
POSTS_YAML = SCRIPT_DIR / "posts.yaml"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

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

def load_template(template_name):
    """Load an HTML template from the templates directory"""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        print(f"⚠️  Template {template_name} not found at {template_path}")
        sys.exit(1)
    return template_path.read_text()

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
        # Use just the filename for post-to-post navigation (we're already in posts/ dir)
        post_filename = Path(post['html']).name
        pdf_link = f'<a href="{Path(post["pdf"]).name}" class="pdf-link" title="Download PDF">📄</a>' if post.get('pdf') else ''
        nav_items += f'''
                <div class="post-item"{active_class}>
                    <a href="{post_filename}">{post['title']}</a>
                    {pdf_link}
                    <div class="post-meta">{datetime.fromisoformat(post['modified']).strftime('%B %d, %Y')}</div>
                </div>'''

    # Load and populate the template
    template = load_template("post.html")
    return template.replace("{{TITLE}}", title) \
                   .replace("{{NAV_ITEMS}}", nav_items) \
                   .replace("{{CONTENT}}", content) \
                   .replace("{{POST_SLUG}}", post_slug) \
                   .replace("{{COMMIT}}", commit)

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
    elif post_format == 'markdown':
        # Read markdown file
        print(f"→ Converting {slug} → HTML...")
        md_content = main_file_path.read_text()

        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])

        # Write HTML fragment
        html_fragment.write_text(f"<body>{html_content}</body>")
        print(f"  ✓ Success")

        # For markdown, we don't generate PDFs (or mark as optional)
        print(f"→ Skipping PDF generation for markdown post")
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
        "pdf": f"posts/{slug}.pdf" if post_format == 'typst' else None,
        "modified": modified,
        "commit": commit,
        "content": fragment_content,
        "format": post_format
    }

    return post_meta

def generate_manifest(posts):
    """Generate a JSON manifest of all posts"""
    # Clean up posts for manifest (remove content field)
    manifest_posts = [{k: v for k, v in p.items() if k != 'content'} for p in posts]
    manifest_path = DOCS_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_posts, indent=2))
    print(f"\n✓ Generated manifest with {len(posts)} posts")

def generate_index(posts):
    """Generate the index.html with post list"""
    # Generate navigation items
    nav_items = ""
    for post in posts:
        pdf_link = f'<a href="{post["pdf"]}" class="pdf-link" title="Download PDF">📄</a>' if post.get('pdf') else ''
        nav_items += f'''
                <div class="post-item">
                    <a href="{post['html']}">{post['title']}</a>
                    {pdf_link}
                    <div class="post-meta">{datetime.fromisoformat(post['modified']).strftime('%B %d, %Y')}</div>
                </div>'''

    # Load and populate the template
    template = load_template("index.html")
    index_html = template.replace("{{NAV_ITEMS}}", nav_items)

    index_path = DOCS_DIR / "index.html"
    index_path.write_text(index_html)
    print(f"✓ Generated index.html")

def copy_static_assets():
    """Copy static CSS, JS, and other assets to docs directory"""
    print("\n📦 Copying static assets...")

    # Define source directory (legacy location)
    static_source = SCRIPT_DIR / "TypstBlog" / "dist"

    # Copy CSS
    css_src = static_source / "css"
    if css_src.exists():
        css_dst = DOCS_DIR / "css"
        shutil.copytree(css_src, css_dst, dirs_exist_ok=True)
        print("  ✓ CSS files copied")

    # Copy JS
    js_src = static_source / "js"
    if js_src.exists():
        js_dst = DOCS_DIR / "js"
        shutil.copytree(js_src, js_dst, dirs_exist_ok=True)
        print("  ✓ JS files copied")

    # Create comments directory
    comments_dst = DOCS_DIR / "comments"
    comments_dst.mkdir(exist_ok=True)
    print("  ✓ Comments directory created")

def check_typst():
    """Check if typst is installed (only needed for typst posts)"""
    result = subprocess.run(
        ["typst", "--version"],
        capture_output=True
    )
    return result.returncode == 0

def main():
    print("🏗️  TypstBlog Builder\n")

    # Load posts configuration
    config = load_posts_yaml()
    post_configs = config['posts']

    if not post_configs:
        print("⚠️  No posts defined in posts.yaml")
        sys.exit(1)

    # Check if typst is needed
    has_typst_posts = any(p.get('format', 'typst') == 'typst' for p in post_configs)
    if has_typst_posts:
        if not check_typst():
            print("⚠️  Typst not found but required for some posts!")
            print("Install it with: curl -fsSL https://typst.app/install.sh | sh")
            print("Or visit: https://github.com/typst/typst")
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

    # Copy static assets
    copy_static_assets()

    print(f"\n✅ Build complete! {len(posts)} post(s) built")
    print(f"   Output: {DOCS_DIR.absolute()}")

if __name__ == "__main__":
    main()
