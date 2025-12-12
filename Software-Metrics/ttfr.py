#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gitpython",
# ]
# ///
#!/usr/bin/env python3
"""
Analyze time-to-first-rework for files in a Git repository.
Tracks when files are first changed and how long until they're changed again.
Only counts actual modifications, not initial file creation.
"""

import git
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import argparse

def analyze_time_to_first_rework(repo_path, branch='HEAD', max_commits=None):
    """
    Analyze how long code lives before being reworked.
    
    Returns:
        dict: Statistics about time-to-first-rework for each file
    """
    repo = git.Repo(repo_path)
    
    # Track when files are created (added to repo)
    file_created = {}  # file_path -> (commit_date, commit_sha)
    
    # Track first modification (after creation)
    first_modification = {}  # file_path -> (commit_date, commit_sha)
    
    # Track rework data (second modification after creation)
    rework_times = defaultdict(list)  # file_path -> [time_deltas]
    
    # Get commits in chronological order (oldest first)
    commits = list(repo.iter_commits(branch, max_count=max_commits))
    commits.reverse()
    
    print(f"Analyzing {len(commits)} commits...")
    
    for i, commit in enumerate(commits):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(commits)} commits...")
        
        # Skip merge commits for cleaner analysis
        if len(commit.parents) > 1:
            continue
            
        commit_date = datetime.fromtimestamp(commit.committed_date)
        
        # Get files changed in this commit
        if commit.parents:
            parent = commit.parents[0]
            diffs = parent.diff(commit)
        else:
            # First commit - all files are new
            diffs = commit.diff(git.NULL_TREE)
        
        for diff in diffs:
            file_path = diff.b_path if diff.b_path else diff.a_path
            
            if not file_path:
                continue
            
            change_type = diff.change_type
            
            # Track file creation (A = Added, but also handle first commit)
            if change_type == 'A' or (not commit.parents):
                if file_path not in file_created:
                    file_created[file_path] = (commit_date, commit.hexsha[:8])
                continue  # Skip to next file - creation doesn't count as "work"
            
            # Handle renames - track as if the renamed file was created now
            if change_type == 'R':
                # For renames, a_path is old name, b_path is new name
                if file_path not in file_created:
                    file_created[file_path] = (commit_date, commit.hexsha[:8])
                continue
            
            # Only process modifications (M) and deletions (D)
            if change_type not in ['M', 'D']:
                continue
            
            # If we haven't seen this file created, treat this as its creation
            # (it existed before our analysis window)
            if file_path not in file_created:
                file_created[file_path] = (commit_date, commit.hexsha[:8])
                continue
            
            # This is a modification to an existing file
            # Is this the first modification after creation?
            if file_path not in first_modification:
                created_date, created_sha = file_created[file_path]
                time_since_creation = commit_date - created_date
                
                # Only track if there's meaningful time difference (> 1 hour)
                if time_since_creation.total_seconds() > 3600:
                    first_modification[file_path] = (commit_date, commit.hexsha[:8])
            else:
                # This is a REWORK (second modification after creation)
                # Only record the FIRST rework
                if file_path not in rework_times:
                    first_mod_date, first_mod_sha = first_modification[file_path]
                    time_delta = commit_date - first_mod_date
                    
                    rework_times[file_path] = [{
                        'time_delta': time_delta,
                        'first_mod_commit': first_mod_sha,
                        'rework_commit': commit.hexsha[:8],
                        'first_mod_date': first_mod_date,
                        'rework_date': commit_date
                    }]
    
    return file_created, first_modification, rework_times

def format_timedelta(td):
    """Format timedelta in human-readable form"""
    days = td.days
    hours = td.seconds // 3600
    
    if days == 0:
        return f"{hours}h"
    elif days < 7:
        return f"{days}d {hours}h"
    elif days < 30:
        weeks = days // 7
        return f"{weeks}w {days % 7}d"
    elif days < 365:
        months = days // 30
        return f"{months}mo {(days % 30) // 7}w"
    else:
        years = days // 365
        months = (days % 365) // 30
        return f"{years}y {months}mo"

def print_statistics(file_created, first_modification, rework_times):
    """Print analysis results"""
    
    total_files = len(file_created)
    modified_files = len(first_modification)
    reworked_files = len(rework_times)
    never_modified = total_files - modified_files
    never_reworked = modified_files - reworked_files
    
    print("\n" + "="*70)
    print("TIME-TO-FIRST-REWORK ANALYSIS")
    print("="*70)
    
    print(f"\nTotal files tracked: {total_files}")
    print(f"Files modified after creation: {modified_files} ({100*modified_files/total_files:.1f}%)")
    print(f"Files reworked (modified 2+ times): {reworked_files} ({100*reworked_files/total_files:.1f}%)")
    print(f"Files never modified: {never_modified} ({100*never_modified/total_files:.1f}%)")
    print(f"Files modified once, never reworked: {never_reworked} ({100*never_reworked/modified_files:.1f}% of modified)")
    
    if not rework_times:
        print("\nNo rework detected in repository history.")
        return
    
    # Calculate statistics
    all_deltas = [data[0]['time_delta'] for data in rework_times.values()]
    all_deltas_sorted = sorted(all_deltas)
    
    avg_delta = sum(all_deltas, timedelta()) / len(all_deltas)
    median_delta = all_deltas_sorted[len(all_deltas_sorted) // 2]
    min_delta = all_deltas_sorted[0]
    max_delta = all_deltas_sorted[-1]
    
    print(f"\n{'Metric':<20} {'Time':<15}")
    print("-" * 35)
    print(f"{'Average:':<20} {format_timedelta(avg_delta):<15}")
    print(f"{'Median:':<20} {format_timedelta(median_delta):<15}")
    print(f"{'Minimum:':<20} {format_timedelta(min_delta):<15}")
    print(f"{'Maximum:':<20} {format_timedelta(max_delta):<15}")
    
    # Percentiles
    print(f"\n{'Percentile':<15} {'Time':<15}")
    print("-" * 30)
    for percentile in [10, 25, 50, 75, 90, 95, 99]:
        idx = int(len(all_deltas_sorted) * percentile / 100)
        print(f"{percentile}th: {format_timedelta(all_deltas_sorted[idx]):<15}")
    
    # Files reworked fastest (top 10)
    print(f"\n{'TOP 10 FASTEST REWORKED FILES'}")
    print("-" * 70)
    fastest = sorted(rework_times.items(), 
                    key=lambda x: x[1][0]['time_delta'])[:10]
    
    for file_path, data in fastest:
        info = data[0]
        print(f"{format_timedelta(info['time_delta']):>8} | {file_path}")
    
    # Files that lived longest before rework (top 10)
    print(f"\n{'TOP 10 MOST STABLE FILES (before first rework)'}")
    print("-" * 70)
    slowest = sorted(rework_times.items(), 
                    key=lambda x: x[1][0]['time_delta'], 
                    reverse=True)[:10]
    
    for file_path, data in slowest:
        info = data[0]
        print(f"{format_timedelta(info['time_delta']):>8} | {file_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze time-to-first-rework in a Git repository'
    )
    parser.add_argument('repo_path', nargs='?', default='.',
                       help='Path to Git repository (default: current directory)')
    parser.add_argument('--branch', default='HEAD',
                       help='Branch to analyze (default: HEAD)')
    parser.add_argument('--max-commits', type=int, default=None,
                       help='Maximum number of commits to analyze')
    parser.add_argument('--min-hours', type=int, default=1,
                       help='Minimum hours between creation and first modification (default: 1)')
    
    args = parser.parse_args()
    
    try:
        file_created, first_modification, rework_times = analyze_time_to_first_rework(
            args.repo_path, 
            args.branch, 
            args.max_commits
        )
        print_statistics(file_created, first_modification, rework_times)
    except git.InvalidGitRepositoryError:
        print(f"Error: '{args.repo_path}' is not a valid Git repository")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()