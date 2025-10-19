from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import ifcopenshell
from ifcopenshell.util.element import copy_deep
import os
import sys



def choose_ifc_pair_from_directory(console, directory, extension=".ifc"):
    # Ensure directory exists
    if not os.path.isdir(directory):
        console.print(f"[red] The directory '{directory}' does not exist.[/red]")
        sys.exit(1)

    # Collect all IFC files
    files = [f for f in os.listdir(directory) if f.lower().endswith(extension.lower())]

    if not files:
        console.print(f"[yellow]⚠️ No {extension} files found in '{directory}'.[/yellow]")
        sys.exit(1)

    # Group files by prefix before -MEP or -ARCH
    groups = {}
    for f in files:
        name = f[:-len(extension)]
        if name.endswith("-MEP"):
            prefix = name.replace("-MEP", "")
            groups.setdefault(prefix, {})["MEP"] = f
        elif name.endswith("-ARCH"):
            prefix = name.replace("-ARCH", "")
            groups.setdefault(prefix, {})["ARCH"] = f
        else:
            # Other IFC files not following the pattern can still be listed
            groups.setdefault(name, {})

    # Display in a table
    table = Table(title=f"Available {extension.upper()} File Pairs in '{directory}'", show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Prefix", style="green")
    table.add_column("MEP File", style="yellow")
    table.add_column("ARCH File", style="magenta")

    prefixes = list(groups.keys())
    for i, prefix in enumerate(prefixes, start=1):
        mep = "✅ " + groups[prefix]["MEP"] if "MEP" in groups[prefix] else "❌ Missing"
        arch = "✅ " + groups[prefix]["ARCH"] if "ARCH" in groups[prefix] else "❌ Missing"
        table.add_row(str(i), prefix, mep, arch)

    console.print()
    console.print(table)
    console.print()

    # Ask user for selection
    while True:
        choice = Prompt.ask("[bold cyan]Enter the number or prefix of the desired file pair[/bold cyan]").strip()

        selected_prefix = None
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(prefixes):
                selected_prefix = prefixes[index - 1]
            else:
                console.print("[red]Invalid number. Please choose one of the listed options.[/red]")
                continue
        else:
            # Try to match by prefix
            matching = [p for p in prefixes if p.lower() == choice.lower()]
            if matching:
                selected_prefix = matching[0]
            else:
                console.print("[red]Invalid input. Please enter a valid number or prefix name.[/red]")
                continue

        # Gather selected files
        mep_path = os.path.join(directory, groups[selected_prefix].get("MEP", ""))
        arch_path = os.path.join(directory, groups[selected_prefix].get("ARCH", ""))

        console.print(f"\n[bold green]Selected prefix:[/bold green] {selected_prefix}")
        console.print(f"MEP file: {mep_path if mep_path else '[red]Missing[/red]'}")
        console.print(f"ARCH file: {arch_path if arch_path else '[red]Missing[/red]'}")

        return mep_path or None, arch_path or None


def choose_ifcElementType(console, ifcFile, category='MEP-HVAC'):


    # dictionary of available checks (only MEP for now)
    category_map = {
        'MEP-HVAC': ['IfcDuctSegment', 'IfcDuctFitting', 'IfcAirTerminal'],
    }

    if category not in category_map:
        console.print(f"[red] Category '{category}' is not recognized.[/red]")
        sys.exit(1)

    catTypes = {catType for catType in category_map[category]}
    # print(f'{catTypes=}')

    # for each type in catTypes, add a list of all present types in the ifc file, and how many there are
    targetElements = []
    counts = {}
    for catType in catTypes:
        check = ifcFile.by_type(catType)
        if check:
            targetElements.extend(check)
            counts[catType] = len(check)
        elif not check:
            counts[catType] = 0
            pass
        else:
            pass

    if not targetElements:
        console.print(f"[yellow]⚠️ No elements of category '{category}' found in the IFC file.[/yellow]")
        sys.exit(1)    

    # Display present types and missing types in a Rich table and show how many there are of each type
    table = Table(title=f"Available Element Types in Category '{category}'", show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Element Type", style="green")
    table.add_column("Count", justify="right", style="magenta")

    for i, (catType, count) in enumerate(counts.items(), start=1):
        table.add_row(str(i), catType, str(count))

    table.add_row("", "[bold yellow]Total Elements Found[/bold yellow]", f"[bold yellow]{len(targetElements)}[/bold yellow]")
    console.print()
    console.print(table)
    console.print()

    # return a list of catTypes
    return targetElements


def copy_space_with_full_metadata(source_space, target_ifc):
    """Copy an IfcSpace including property and quantity sets."""
    new_space = copy_deep(target_ifc, source_space)

    # Copy all property/quantity sets (Psets + QSets)
    for rel in getattr(source_space, "IsDefinedBy", []):
        propdef = rel.RelatingPropertyDefinition
        new_propdef = target_ifc.add(propdef)

        target_ifc.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[new_space],
            RelatingPropertyDefinition=new_propdef,
            Name=rel.Name,
            Description=rel.Description
        )

    return target_ifc, new_space


def merge_spaces_with_quantities_and_structure(console, source_ifc, target_ifc):
    """Copy all spaces (with Psets/QSets)."""
    copied_spaces = []

    for source_space in source_ifc.by_type("IfcSpace"):
        target_ifc, new_space = copy_space_with_full_metadata(source_space, target_ifc)

        copied_spaces.append(new_space)

    console.print(f"Copied {len(copied_spaces)} spaces with quantities.")
    return target_ifc, copied_spaces


def writeReport(console, misplacedElements):
    # write misplacedElements into text file
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")
    console.print(f"[bold green]Writing report to outputFiles/misplacedElements_REPORT_{dt_string}...[/bold green]")
    with open(f"outputFiles/misplacedElements_REPORT_{dt_string}.txt", "w") as f:
        f.write(f"Misplaced Elements Report - Generated on {dt_string}\n")
        f.write("========================================\n")
        f.write(f"""\n Overview of potentially misplaced elements:\n
Total elements potentially misplaced: {len(misplacedElements[0]) + len(misplacedElements[1])}
- Elements potentially placed on the wrong level: {len(misplacedElements[0])}
- Elements placed between levels (Should potentially be moved to building): {len(misplacedElements[1])}
\n========================================\n\n""")

        f.write("⚠️ Elements potentially placed on the wrong level ⚠️:\n")
        for element in misplacedElements[0]:
            f.write(f"Element {element['elementID']} (Type: {element['elementType']})\n")
            f.write(f"  Original Level: {element['originalLevel']} ({element['originalLevelElevation']} m)\n")
            f.write(f"  New Level: {element['newLevel']} ({element['newLevelElevation']} m)\n")
            f.write(f"  Element Height: {element['elementHeight']} m\n")
            f.write(f"  Min Z: {element['minZ']} m\n")
            f.write(f"  Max Z: {element['maxZ']} m\n")
            f.write("\n")

        f.write("\n========================================\n\n")
        f.write("⛔ Elements placed between levels (Should potentially be moved to building) ⛔:\n")
        for element in misplacedElements[1]:
            f.write(f"Element {element['elementID']} (Type: {element['elementType']})\n")
            f.write(f"  Original Level: {element['originalLevel']} ({element['originalLevelElevation']} m)\n")
            f.write(f"  New Representation: {element['newRepresentation']}\n")
            f.write(f"  Element Height: {element['elementHeight']} m\n")
            f.write(f"  Min Z: {element['minZ']} m\n")
            f.write(f"  Max Z: {element['maxZ']} m\n")
            f.write("\n")
        f.write("\n========================================\n\n")
        f.close()