#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmt",
#     "logfmter",
#     "rich",
# ]
# ///

from slap import read_logs
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from collections import Counter

console = Console()

# Read all logs (from stdin or files)
log_snapshot = read_logs()

# Extract data from logs
discovered_files = log_snapshot.get('File Discovered', [])
stat_entries = log_snapshot.get('File Stat Collected', [])
hash_entries = log_snapshot.get('File Hash Collected', [])

console.print("\n[bold cyan]═══ File System Analysis ═══[/bold cyan]\n")

# Basic counts
console.print(Panel(
    f"[green]Files Discovered:[/green] {len(discovered_files)}\n"
    f"[green]Files Stat'd:[/green] {len(stat_entries)}\n"
    f"[green]Files Hashed:[/green] {len(hash_entries)}",
    title="[bold]Overview[/bold]",
    border_style="cyan"
))

if stat_entries:
    # File size statistics
    sizes = [int(entry['size_bytes']) for entry in stat_entries if 'size_bytes' in entry]

    if sizes:
        total_size = sum(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        avg_size = total_size / len(sizes)

        def format_bytes(bytes_val):
            """Convert bytes to human-readable format"""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_val < 1024.0:
                    return f"{bytes_val:.2f} {unit}"
                bytes_val /= 1024.0
            return f"{bytes_val:.2f} PB"

        console.print(Panel(
            f"[yellow]Total Size:[/yellow] {format_bytes(total_size)}\n"
            f"[yellow]Min Size:[/yellow] {format_bytes(min_size)}\n"
            f"[yellow]Max Size:[/yellow] {format_bytes(max_size)}\n"
            f"[yellow]Avg Size:[/yellow] {format_bytes(avg_size)}",
            title="[bold]File Size Statistics[/bold]",
            border_style="yellow"
        ))

    # File type distribution
    extensions = [str(entry['extension']) if entry['extension'] else "" for entry in stat_entries if 'extension' in entry]
    ext_counter = Counter(extensions)

    if ext_counter:
        table = Table(title="[bold]File Type Distribution[/bold]", show_header=True, header_style="bold magenta")
        table.add_column("Extension", style="cyan", width=20)
        table.add_column("Count", justify="right", style="green")
        table.add_column("Percentage", justify="right", style="yellow")

        total_files = len(extensions)
        for ext, count in ext_counter.most_common(15):
            percentage = (count / total_files) * 100
            display_ext = ext if ext else "(no extension)"
            table.add_row(str(display_ext), str(count), f"{percentage:.1f}%")

        console.print(table)

        if len(ext_counter) > 15:
            console.print(f"[dim]... and {len(ext_counter) - 15} more extension types[/dim]\n")

if hash_entries:
    # Duplicate detection
    hashes = [entry['hash'] for entry in hash_entries if 'hash' in entry]
    hash_counter = Counter(hashes)
    duplicates = {h: count for h, count in hash_counter.items() if count > 1}

    if duplicates:
        total_duplicate_files = sum(count for count in duplicates.values())
        unique_duplicate_content = len(duplicates)
        wasted_copies = total_duplicate_files - unique_duplicate_content

        # Calculate wasted space
        if stat_entries:
            hash_to_size = {}
            for stat_entry in stat_entries:
                for hash_entry in hash_entries:
                    if stat_entry['entry'] == hash_entry['entry']:
                        hash_to_size[hash_entry['hash']] = int(stat_entry.get('size_bytes', 0))
                        break

            wasted_space = sum(
                hash_to_size.get(h, 0) * (count - 1)
                for h, count in duplicates.items()
            )

            console.print(Panel(
                f"[red]Unique Duplicate Content:[/red] {unique_duplicate_content}\n"
                f"[red]Total Duplicate Files:[/red] {total_duplicate_files}\n"
                f"[red]Extra Copies:[/red] {wasted_copies}\n"
                f"[red]Wasted Space:[/red] {format_bytes(wasted_space)}",
                title="[bold]Duplicate Analysis[/bold]",
                border_style="red"
            ))

            # Show top duplicates
            if duplicates:
                table = Table(title="[bold]Top Duplicated Files[/bold]", show_header=True, header_style="bold red")
                table.add_column("Hash (first 16)", style="dim", width=18)
                table.add_column("Copies", justify="right", style="red")
                table.add_column("Size Each", justify="right", style="yellow")
                table.add_column("Total Wasted", justify="right", style="magenta")
                table.add_column("Example File", style="cyan", no_wrap=False)

                sorted_dupes = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]
                for hash_val, count in sorted_dupes:
                    size = hash_to_size.get(hash_val, 0)
                    wasted = size * (count - 1)

                    # Find one of the files with this hash
                    example_file = next(
                        (entry['entry'] for entry in hash_entries if entry.get('hash') == hash_val),
                        "N/A"
                    )

                    table.add_row(
                        hash_val[:16],
                        str(count),
                        format_bytes(size),
                        format_bytes(wasted),
                        example_file
                    )

                console.print(table)
    else:
        console.print(Panel(
            "[green]No duplicate files found! 🎉[/green]",
            title="[bold]Duplicate Analysis[/bold]",
            border_style="green"
        ))

console.print()
