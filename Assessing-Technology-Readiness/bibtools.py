#!/usr/bin/env python3
"""Bibliography management tools for research.yaml"""

import typer
import yaml
import questionary
import subprocess
from pathlib import Path
from typing import Optional

app = typer.Typer(help="Tools for managing research bibliography")


@app.command()
def bibstat(
    file: Path = typer.Argument(
        "research.yaml",
        help="Path to research YAML file"
    )
):
    """Show statistics about the bibliography entries"""

    if not file.exists():
        typer.echo(f"Error: File not found: {file}", err=True)
        raise typer.Exit(1)

    # Load YAML file
    with open(file, 'r') as f:
        data = yaml.safe_load(f)

    # Count entries
    sources = data.get('sources', {})
    total_entries = len(sources)

    # Count insights
    total_insights = sum(
        len(source.get('insights', []))
        for source in sources.values()
    )

    # Count by source type
    source_types = {}
    for source in sources.values():
        source_type = source.get('source_type', 'unknown')
        source_types[source_type] = source_types.get(source_type, 0) + 1

    # Display stats
    typer.echo(f"📚 Bibliography Statistics")
    typer.echo(f"=" * 40)
    typer.echo(f"Total entries: {total_entries}")
    typer.echo(f"Total insights: {total_insights}")
    typer.echo(f"Average insights per entry: {total_insights / total_entries:.1f}")
    typer.echo()
    typer.echo("By source type:")
    for source_type, count in sorted(source_types.items()):
        typer.echo(f"  {source_type}: {count}")


@app.command()
def browse(
    file: Path = typer.Argument(
        "research.yaml",
        help="Path to research YAML file"
    )
):
    """Interactively browse bibliography entries and open in lynx"""

    if not file.exists():
        typer.echo(f"Error: File not found: {file}", err=True)
        raise typer.Exit(1)

    # Load YAML file
    with open(file, 'r') as f:
        data = yaml.safe_load(f)

    sources = data.get('sources', {})

    if not sources:
        typer.echo("No sources found in the bibliography")
        raise typer.Exit(1)

    while True:
        # Create choices with title and insights preview
        choices = []
        source_map = {}

        for key, source in sources.items():
            title = source.get('title', 'Untitled')
            insights = source.get('insights', [])
            insight_count = len(insights)

            # Create a display string with title and insight count
            display = f"{title} ({insight_count} insights)"
            choices.append(display)
            source_map[display] = (key, source)

        # Add exit option
        choices.append("Exit")

        # Show selection menu
        selection = questionary.select(
            "Select a source to view (↑↓ to navigate, Enter to select):",
            choices=choices
        ).ask()

        if selection is None or selection == "Exit":
            typer.echo("Goodbye!")
            break

        # Get selected source
        key, source = source_map[selection]

        # Show details
        title = source.get('title', 'Untitled')
        link = source.get('link', 'No link')
        authors = source.get('authors', [])
        insights = source.get('insights', [])

        typer.echo()
        typer.echo("=" * 60)
        typer.echo(f"Title: {title}")
        typer.echo(f"Authors: {', '.join(authors)}")
        typer.echo(f"Link: {link}")
        typer.echo()
        typer.echo("Insights:")
        for i, insight in enumerate(insights, 1):
            typer.echo(f"  {i}. {insight}")
        typer.echo("=" * 60)
        typer.echo()

        # Ask if user wants to open in lynx
        open_link = questionary.confirm(
            "Open this link in lynx?",
            default=True
        ).ask()

        if open_link:
            try:
                subprocess.run(['lynx', link])
            except FileNotFoundError:
                typer.echo("Error: lynx not found. Please install lynx to browse URLs.", err=True)
            except Exception as e:
                typer.echo(f"Error opening lynx: {e}", err=True)


if __name__ == "__main__":
    app()
