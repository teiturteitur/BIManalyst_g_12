from datetime import datetime
import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import inspect
import ifcopenshell
from ifcopenshell.util.element import copy_deep
import ifcopenshell.util.shape
from ifcopenshell.util.file import IfcHeaderExtractor
from .functions import get_element_bbox
from bcf.v3.bcfxml import BcfXml
import bcf.v3.visinfo
import bcf.v3.model
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
        console.print(f"[yellow]Please add IFC files ending with '-MEP.ifc' and '-ARCH.ifc' to {directory} and try again.[/yellow]")
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

    console.print('\n[bold yellow]Please make sure to select a MEP/ARCH file pair from the list below:[/bold yellow]')

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
        
        # if arch file missing, check if spaces are in mep file
        if "ARCH" not in groups[selected_prefix]:
            mep_file_path = os.path.join(directory, groups[selected_prefix].get("MEP", ""))
            mep_ifc = ifcopenshell.open(mep_file_path)
            spaces = mep_ifc.by_type("IfcSpace")
            if not spaces:
                console.print(f"[red]The selected ARCH file is missing and no IfcSpaces found in the MEP file '{groups[selected_prefix].get('MEP', '')}'. Please select a different pair.[/red]")
                continue
        if "MEP" not in groups[selected_prefix]:
            console.print(f"[red]The selected MEP file is missing. Please select a different pair.[/red]")
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
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat() + "Z"

def cameraSetup(element: ifcopenshell.entity_instance,
                ifc_file: ifcopenshell.file) -> tuple[list[float], list[float], list[float]]:
    # print(f'Creating camera setup for element {element.GlobalId}')
    bbox = get_element_bbox(element)
    # print(f'{bbox=}')
    center = [(bbox['min'][i] + bbox['max'][i]) / 2 for i in range(3)]

    camera_view_point = [float(bbox['max'][0]*1.04), float(bbox['max'][1]*1.04), float(bbox['max'][2]*1.075)]
    camera_direction = [float(center[0] - camera_view_point[0]),
                       float(center[1] - camera_view_point[1]),
                       float(center[2] - camera_view_point[2])]
    camera_up_vector = [0.0, 0.0, 1.0]

    return camera_view_point, camera_direction, camera_up_vector

def add_issue(bcf_obj: BcfXml, title: str, message: str, 
              author: str, element: ifcopenshell.entity_instance, ifc_file: ifcopenshell.file,
              bcf_path: str, bcf_zip: bcf.v3.visinfo.ZipFileInterface) -> None:
    th = bcf_obj.add_topic(
        title,
        message,
        author,
        "Parameter Validation",
    )
    
    visinfo_handler = th.add_viewpoint(element)
    # visinfo_handler.create_from_point_and_guids(position=[5,10,1])
    visinfo_handler.set_selected_elements([element])
    # visinfo_handler.set_visible_elements([element])

    camera_view_point, camera_direction, camera_up_vector = cameraSetup(element=element, ifc_file=ifc_file)
    visinfo_handler.visualization_info.perspective_camera = bcf.v3.visinfo.build_camera_from_vectors(camera_position=camera_view_point, camera_dir=camera_direction, camera_up=camera_up_vector)
    # inspect(visinfo_handler) # FOR DEBUGGING  

    th.comments = [bcf.v3.model.Comment(
        guid=str(uuid.uuid4()),
        date=iso_now(),
        author=author,
        comment=message,
        viewpoint=bcf.v3.model.CommentViewpoint(guid=visinfo_handler.guid),
    )]

    


def generate_bcf_from_errors(
    console: Console,
    ifc_file: ifcopenshell.file,
    ifc_file_path: str,
    misplacedElements: list,
    missingAHUsystems: dict,
    unassignedTerminals: dict,
    output_bcf: str = "hvac_issues.bcfzip") -> None:
    """
    Automatically writes a BCF file listing coordination issues:
      - misplacedElements: list of dicts with keys ['elementID', 'elementType', 'originalLevel', 'newLevel', ...]
      - missingAHUsystems: dict keyed by system name with ['ElementCount', 'ElementTypes', 'ElementIDs']
      - unassignedTerminals: dict keyed by flow direction, each containing list of GUIDs
    """ 

    console.print("🔧 Opening IFC file...")
    extractor = IfcHeaderExtractor(ifc_file_path)
    header_info = extractor.extract()
    console.print("📦 Creating new BCF project...")
    bcf_project = BcfXml.create_new(project_name=header_info.get('name'))
    bcf_project.save(filename=output_bcf, keep_open=True)
    bcf_zip = bcf_project._zip_file
    # misplaced elements
    console.print("🧱 Adding misplaced element topics...")
    for error_category, elements in misplacedElements.items():
        for guid, e in elements.items():
            # print(f'{guid=},{e['element']=}')
            # title = f'{e.get("elementType", "Unknown")} Element represented on the wrong level: {guid}'
            title = f"{error_category}: {e.get('elementType', 'Unknown')} representation issue - {guid}"
            desc_lines = [
                f"Element Type: {e.get('elementType', 'Unknown')}",
                f"Issue Category: {error_category}",
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

            add_issue(bcf_obj=bcf_project, title=title, message=desc, author="HVAC-Checker", 
                      element=ifc_file.by_id(guid), ifc_file=ifc_file, bcf_path=output_bcf, bcf_zip=bcf_zip)



    # systems missing AHUs
    console.print("💨 Adding missing AHU system topics...")
    for sys_name, info in missingAHUsystems.items():
        title = f"IfcDistributionSystem - {sys_name}: Missing Air Handling Unit"
        desc = (
            f"The distribution system '{sys_name}' contains {info.get('ElementCount', 0)} elements "
            f"but no AHU (IfcUnitaryUnit) was found.\n"
            f"Types: {info.get('ElementTypes', 'Unknown')}."
        )
        # topic = bcf_project.add_topic(
        #     title=title,
        #     description=desc,
        #     author="HVAC-Checker",
        #     topic_type='Issue',
        #     topic_status='Open'
        # )

        systemElements = info.get('Elements', [])
        if systemElements:
            # camera_view_point, camera_direction, camera_up_vector = cameraSetup(element=systemElements[0], ifc_file=ifc_file)
            # viewpoint = topic.add_viewpoint_from_point_and_guids(position=camera_view_point, guids=systemElements)
            add_issue(bcf_obj=bcf_project, title=title, message=desc, author="HVAC-Checker", 
                      element=systemElements, ifc_file=ifc_file, bcf_path=output_bcf, bcf_zip=bcf_zip)
            # viewpoint.save()

    # unassigned air terminals
    console.print("🌬️ Adding unassigned terminal topics...")
    for flow_dir, element_list in unassignedTerminals.items():
        for element in element_list:
            title = f"Air terminal not placed inside a space - ({element})"
            desc = f"Air terminal {element} - {flow_dir} is not located inside an IfcSpace."
            
            # topic = bcf_project.add_topic(
            #     title=title,
            #     description=desc,
            #     author="HVAC-Checker",
            #     topic_type='Issue',
            #     topic_status='Open'
            # )

            # camera_view_point, camera_direction, camera_up_vector = cameraSetup(element, ifc_file)
            # camera =bcf.v3.visinfo.build_camera_from_vectors(camera_position=camera_view_point, camera_dir=camera_direction, camera_up=camera_up_vector)

            add_issue(bcf_obj=bcf_project, title=title, message=desc, author="HVAC-Checker", 
                      element=ifc_file.by_id(element), ifc_file=ifc_file, bcf_path=output_bcf, bcf_zip=bcf_zip)
            # viewpoint = topic.add_viewpoint_from_point_and_guids(position=camera_view_point, guids=[element])
            # viewpoint.set_hidden_elements(['IfcSpace'])  # hide spaces
            # viewpoint = topic.add_viewpoint(element=ifc_file.by_id(element))
            # viewpoint.setup_camera(camera_view_point, camera_direction, camera_up_vector)
            # viewpoint.save()

    # save the BCF file
    bcf_project.save(filename=output_bcf)
    console.print(f"✅ BCF file successfully written: {output_bcf}")

