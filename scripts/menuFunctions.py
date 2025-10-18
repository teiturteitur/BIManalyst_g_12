from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import os
import sys


def choose_file_from_directory(console, directory, extension=".ifc", exceptions=[]):
    # Ensure directory exists
    if not os.path.isdir(directory):
        console.print(f"[red] The directory '{directory}' does not exist.[/red]")
        sys.exit(1)

    # Get IFC files
    files = [f for f in os.listdir(directory) if f.lower().endswith(extension.lower())]
    files = [f for f in files if f not in exceptions]

    # If no files found, stop
    if not files:
        console.print(f"[yellow]⚠️ No {extension} files found in '{directory}'.[/yellow]")
        console.print("Please add valid files and run the script again.")
        sys.exit(1)

    # Display files in a Rich table
    table = Table(title=f"Available {extension.upper()} Files in /{directory}", show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("File Name", style="green")

    for i, f in enumerate(files, start=1):
        table.add_row(str(i), f)

    console.print()
    console.print(table)
    console.print()

    # Ask until valid input
    while True:
        choice = Prompt.ask("[bold cyan]Enter the number or name of the file[/bold cyan]").strip()

        # If user typed a number
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(files):
                selected = os.path.join(directory, files[index - 1])
                console.print(f"\n[bold green] Selected file:[/bold green] {selected}")
                return selected
            else:
                console.print("[red] Invalid number. Please choose one of the listed options.[/red]")

        # If user typed a file name
        elif choice.lower() in [f.lower() for f in files]:
            matched_file = next(f for f in files if f.lower() == choice.lower())
            selected = os.path.join(directory, matched_file)
            console.print(f"\n[bold green] Selected file:[/bold green] {selected}")
            return selected

        else:
            console.print("[red] Invalid input. Please enter a valid number or file name.[/red]")
