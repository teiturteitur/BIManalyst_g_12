from datetime import datetime
import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import ifcopenshell
from ifcopenshell.util.element import copy_deep
from bcf.v2.bcfxml import BcfXml
import os
import sys
import uuid



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



def iso_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def generate_bcf_from_errors(
    console: Console,
    ifc_file,
    misplacedElements: list,
    missingAHUsystems: dict,
    unassignedTerminals: dict,
    output_bcf: str = "hvac_issues.bcfzip"
):
    """
    Automatically writes a BCF file listing coordination issues:
      - misplacedElements: list of dicts with keys ['elementID', 'elementType', 'originalLevel', 'newLevel', ...]
      - missingAHUsystems: dict keyed by system name with ['ElementCount', 'ElementTypes', 'ElementIDs']
      - unassignedTerminals: dict keyed by flow direction, each containing list of GUIDs
    """

    console.print("🔧 Opening IFC file...")
    model = ifc_file

    console.print("📦 Creating new BCF project...")
    bcf_project = BcfXml.create_new(project_name="HVAC Coordination Issues")

    # misplaced elements
    console.print("🧱 Adding misplaced element topics...")
    for category_name, elements in misplacedElements.items():
        for guid, e in elements.items():
            title = f"{category_name}: {e.get('elementType', 'Unknown')}"
            desc_lines = [
                f"Element: {guid}",
                f"Type: {e.get('elementType', 'Unknown')}",
                f"Issue Category: {category_name}",
            ]

            # Add more context if fields exist
            if "originalLevel" in e and "newLevel" in e:
                desc_lines.append(
                    f"Moved from {e['originalLevel']} (elev {e.get('originalLevelElevation')}) "
                    f"to {e['newLevel']} (elev {e.get('newLevelElevation')})."
                )
            if "minZ" in e and "maxZ" in e:
                desc_lines.append(
                    f"Min Z: {e['minZ']}, Max Z: {e['maxZ']}, Height: {e.get('elementHeight')}"
                )

            desc = "\n".join(desc_lines)

            topic = bcf_project.add_topic(
                title=title,
                description=desc,
                author="HVAC-Checker",
            )

            # if guid:
            #     topic.add_reference(reference_type="IfcElement", ifc_guid=guid)


    # systems missing AHUs
    console.print("💨 Adding missing AHU system topics...")
    for sys_name, info in missingAHUsystems.items():
        title = f"System {sys_name}: Missing Air Handling Unit"
        desc = (
            f"The distribution system '{sys_name}' contains {info.get('ElementCount', 0)} elements "
            f"but no AHU (IfcUnitaryUnit) was found.\n"
            f"Types: {info.get('ElementTypes', 'Unknown')}."
        )
        topic = bcf_project.add_topic(
            title=title,
            description=desc,
            author="HVAC-Checker"
        )
        # # Optionally link one representative element
        # if info.get("ElementIDs"):
        #     topic.add_reference(reference_type="IfcElement", ifc_guid=info["ElementIDs"][0])

    # unassigned air terminals
    console.print("🌬️ Adding unassigned terminal topics...")
    for flow_dir, guid_list in unassignedTerminals.items():
        for guid in guid_list:
            title = f"Air terminal not placed in a space ({flow_dir})"
            desc = f"Air terminal {guid} with flow direction '{flow_dir}' is not located inside an IfcSpace."
            topic = bcf_project.add_topic(
                title=guid,
                description=desc,
                author="HVAC-Checker"
            )
            # topic.add_reference(reference_type="IfcElement", ifc_guid=guid)

    # save the BCF file
    bcf_project.save(output_bcf)
    console.print(f"✅ BCF file successfully written: {output_bcf}")

