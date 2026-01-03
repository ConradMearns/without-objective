#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "dspy-ai",
#     "openai",
#     "rich",
#     "python-dotenv",
# ]
# ///

"""
Interactive file editor powered by DSPy.
Based on principles from: https://fabianhertwig.com/blog/coding-assistants-file-edits/

Usage:
    ./file_editor.py

Then follow the prompts to edit or create files.
"""

import os
import sys
from pathlib import Path
from difflib import unified_diff
from typing import Optional

import dspy
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Load environment variables from .env file
load_dotenv()

console = Console()


class FileEditSignature(dspy.Signature):
    """Generate file edits using search/replace blocks."""

    file_path: str = dspy.InputField(desc="Path to the file")
    file_content: str = dspy.InputField(desc="Current file content (empty if new file)")
    user_instruction: str = dspy.InputField(desc="What the user wants to do")

    edit_blocks: str = dspy.OutputField(
        desc="Edit blocks in format:\n<<<SEARCH\n[exact text to find]\n===\n[replacement text]\n>>>SEARCH\nMultiple blocks allowed. For new files, use empty SEARCH block."
    )


class FileEditor:
    def __init__(self):
        # Initialize DSPy with OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        model = os.getenv("MODEL", "openai/gpt-4o-mini")

        # Ensure model has openrouter/ prefix for proper routing
        if not model.startswith("openrouter/"):
            model = f"openrouter/{model}"

        lm = dspy.LM(
            model=model,
            api_key=api_key,
        )
        dspy.configure(lm=lm)

        self.editor_module = dspy.ChainOfThought(FileEditSignature)

    def read_file(self, file_path: Path) -> str:
        """Read file content, return empty string if doesn't exist."""
        if file_path.exists():
            return file_path.read_text()
        return ""

    def parse_edit_blocks(self, edit_blocks_str: str) -> list[tuple[str, str]]:
        """Parse edit blocks into (search, replace) tuples."""
        blocks = []
        lines = edit_blocks_str.split('\n')

        i = 0
        while i < len(lines):
            if lines[i].strip() == '<<<SEARCH':
                # Find the separator
                search_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() != '===':
                    search_lines.append(lines[i])
                    i += 1

                # Find the end marker
                replace_lines = []
                i += 1  # Skip ===
                while i < len(lines) and lines[i].strip() != '>>>SEARCH':
                    replace_lines.append(lines[i])
                    i += 1

                search = '\n'.join(search_lines)
                replace = '\n'.join(replace_lines)
                blocks.append((search, replace))
            i += 1

        return blocks

    def fuzzy_find_and_replace(self, content: str, search: str, replace: str) -> Optional[str]:
        """
        Apply search/replace with fuzzy matching strategy:
        1. Try exact match
        2. Try whitespace-normalized match
        3. Try fuzzy line-by-line match
        """
        # Strategy 1: Exact match
        if search in content:
            return content.replace(search, replace, 1)

        # Strategy 2: Whitespace-normalized (collapse multiple spaces/tabs)
        import re

        def normalize_ws(text):
            return re.sub(r'\s+', ' ', text)

        norm_search = normalize_ws(search)
        norm_content = normalize_ws(content)

        if norm_search in norm_content:
            # Find position in normalized, map back to original
            idx = norm_content.index(norm_search)
            # This is approximate - for now just do simple replacement
            return content.replace(search.strip(), replace.strip(), 1)

        # Strategy 3: Fuzzy matching - find best matching block
        from difflib import SequenceMatcher

        search_lines = search.strip().split('\n')
        content_lines = content.split('\n')

        best_ratio = 0.0
        best_pos = -1

        for i in range(len(content_lines) - len(search_lines) + 1):
            block = '\n'.join(content_lines[i:i+len(search_lines)])
            ratio = SequenceMatcher(None, search.strip(), block).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_pos = i

        # If we found a good enough match (>0.8 similarity)
        if best_ratio > 0.8 and best_pos >= 0:
            result_lines = (
                content_lines[:best_pos] +
                replace.split('\n') +
                content_lines[best_pos + len(search_lines):]
            )
            return '\n'.join(result_lines)

        return None

    def apply_edits(self, content: str, edit_blocks: list[tuple[str, str]]) -> tuple[bool, str, str]:
        """
        Apply edit blocks to content.
        Returns: (success, new_content, error_message)
        """
        result = content

        for i, (search, replace) in enumerate(edit_blocks):
            # Handle new file case (empty search)
            if not search.strip() and not content:
                result = replace
                continue

            new_result = self.fuzzy_find_and_replace(result, search, replace)

            if new_result is None:
                error = f"Edit block {i+1} failed: Could not find match for:\n{search[:200]}"
                return False, result, error

            result = new_result

        return True, result, ""

    def show_diff(self, original: str, modified: str, file_path: Path):
        """Display unified diff using rich."""
        diff = unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        )

        diff_text = ''.join(diff)

        if not diff_text:
            console.print("[yellow]No changes detected[/yellow]")
            return

        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Proposed Changes", border_style="cyan"))

    def edit_file(self, file_path: str, instruction: str):
        """Main editing workflow."""
        path = Path(file_path).resolve()

        console.print(f"\n[bold cyan]File:[/bold cyan] {path}")
        console.print(f"[bold cyan]Instruction:[/bold cyan] {instruction}\n")

        # Read current content
        original_content = self.read_file(path)

        if original_content:
            console.print(f"[green]File exists ({len(original_content)} chars)[/green]")
        else:
            console.print("[yellow]File does not exist - will create new[/yellow]")

        # Generate edits using DSPy
        console.print("[dim]Generating edits...[/dim]")

        try:
            result = self.editor_module(
                file_path=str(path),
                file_content=original_content,
                user_instruction=instruction
            )

            edit_blocks_str = result.edit_blocks

            # Show raw edit blocks for debugging
            console.print("\n[dim]Edit blocks:[/dim]")
            console.print(Panel(edit_blocks_str, border_style="dim"))

            # Parse and apply edits
            blocks = self.parse_edit_blocks(edit_blocks_str)
            console.print(f"\n[dim]Parsed {len(blocks)} edit block(s)[/dim]")

            success, new_content, error = self.apply_edits(original_content, blocks)

            if not success:
                console.print(f"[bold red]Error:[/bold red] {error}")
                return

            # Show diff
            self.show_diff(original_content, new_content, path)

            # Confirm and apply
            if Confirm.ask("\nApply these changes?", default=True):
                # Create parent directories if needed
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(new_content)
                console.print(f"[bold green]✓[/bold green] Changes applied to {path}")
            else:
                console.print("[yellow]Changes discarded[/yellow]")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            import traceback
            console.print(traceback.format_exc())


def main():
    console.print(Panel.fit(
        "[bold cyan]PNF Editor[/bold cyan]\n"
        "Powered by DSPy\n"
        "Type 'quit' or 'exit' to stop",
        border_style="cyan"
    ))

    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENROUTER_API_KEY not found in .env file")
        console.print("[dim]Copy .env.example to .env and add your API key[/dim]")
        sys.exit(1)

    try:
        editor = FileEditor()
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    while True:
        console.print("\n" + "─" * 80 + "\n")

        # Get file path
        file_path = Prompt.ask("[bold]File path[/bold]")

        if file_path.lower() in ['quit', 'exit', 'q']:
            console.print("[cyan]Goodbye![/cyan]")
            break

        # Get instruction
        instruction = Prompt.ask("[bold]What do you want to do?[/bold]")

        if instruction.lower() in ['quit', 'exit', 'q']:
            console.print("[cyan]Goodbye![/cyan]")
            break

        # Execute edit
        editor.edit_file(file_path, instruction)


if __name__ == "__main__":
    main()
