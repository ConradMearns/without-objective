#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyyaml",
#     "gitpython",
# ]
# ///

import yaml
from pathlib import Path
from git import Repo
from datetime import datetime

def get_post_file_path(post):
    """Resolve the full file path for a post."""
    source = post.get('source', '.')
    main_file = post.get('main_file', '')

    # Handle relative paths
    if source == '.' or source == './':
        return Path(main_file)
    else:
        return Path(source) / main_file

def get_commit_history(repo, file_path, limit=10):
    """Get commit history for a specific file."""
    commits = []

    try:
        # Get commits that touched this file
        for commit in repo.iter_commits(paths=str(file_path), max_count=limit):
            commits.append({
                'hash': commit.hexsha[:7],
                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'author': commit.author.name,
                'message': commit.message.strip().split('\n')[0]  # First line only
            })
    except Exception as e:
        print(f"Warning: Could not get history for {file_path}: {e}")

    return commits

def main():
    # Load posts.yaml
    posts_file = Path('posts.yaml')
    with open(posts_file, 'r') as f:
        data = yaml.safe_load(f)

    # Initialize git repo
    repo = Repo('.')

    # Collect history for each post
    post_history = {}

    for post in data.get('posts', []):
        slug = post['slug']
        file_path = get_post_file_path(post)

        print(f"Collecting history for {slug} ({file_path})...")
        commits = get_commit_history(repo, file_path)

        post_history[slug] = {
            'file': str(file_path),
            'commits': commits
        }

    # Write output
    output_file = Path('post_history.yaml')
    with open(output_file, 'w') as f:
        yaml.dump(post_history, f, default_flow_style=False, sort_keys=False)

    print(f"\nHistory written to {output_file}")
    print(f"Total posts processed: {len(post_history)}")

if __name__ == '__main__':
    main()
