'''
This function analyzes the IfcBuildingSystems in an IFC file and checks if any of them are missing an air handling unit (AHU) element.

if an IfcBuildingSystem does NOT contain an AHU element, it will be reported as output.



*NOT IMPLEMENTED YET* 
All IfcBuildingSystems _CONTAINING_ an AHU element will be further analyzed, to check if the system is dimensioned correctly for the required air flow. 
*NOT IMPLEMENTED YET*


Authors: s214310, s203493, s201348
'''


import ifcopenshell
import ifcopenshell.util.system
import ifcopenshell.util.pset
import ifcopenshell.api
import ifcopenshell.geom
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import numpy as np



def systemAnalyzer(console, ifc_file, targetSystems='IfcDistributionSystem'):

    # build dictionaries of systems with and without AHUs. 

    identifiedSystems = {}

    ifc_file_systems = ifc_file.by_type(targetSystems)
    # if system.Name does not contain VU or VI, remove it from the list
    ifc_file_systems = [system for system in ifc_file_systems if 'VU' in system.Name or 'VI' in system.Name]


    missingAHUsystems = {}
    for system in ifc_file_systems:
        elements = system.IsGroupedBy[0].RelatedObjects

        uniqueElements = set(elements.is_a() for elements in elements)
        uniqueElementsType = set(elements.ObjectType for elements in elements)

        # the AHU element _should_ be an IfcUnitaryEquipment, but in the given ifc files, they are IfcBuildingElementProxy containing 'Geniox' in their names.
        # in the future, this should just create an instance in the BCF file saying that the system is missing an AHU element.
        if any(e and 'IfcUnitaryEquipment' in e for e in uniqueElements):
            identifiedSystems[system.Name] = {'ElementCount': len(elements), 'Elements': list(uniqueElements), 'ElementIDs': [elements[i].GlobalId for i in range(len(elements))]}
        else:
            # if uniqueElements contains IfcBuildingElementProxy with 'Geniox' in their ObjectType, consider it as having an AHU - remove this in future
            if any('Geniox' in str(e) for e in uniqueElementsType):
                identifiedSystems[system.Name] = {'ElementCount': len(elements), 'ElementTypes': list(uniqueElements), 'ElementIDs': [elements[i].GlobalId for i in range(len(elements))]}
            else:
                missingAHUsystems[system.Name] = {'ElementCount': len(elements), 'ElementTypes': list(uniqueElements), 'ElementIDs': [elements[i].GlobalId for i in range(len(elements))]}

    # for all identified systems, find the Supply/Return pairs (the systems using the same AHU) and add a new key 'PairedSystem' to the dictionary
    for systemName, info in identifiedSystems.items():
        elements = info.get("ElementIDs", [])
        ahu_elements = [el for el in elements if ifc_file.by_id(el).is_a("IfcUnitaryEquipment") or ('Geniox' in str(ifc_file.by_id(el).ObjectType))]
        pairedSystems = []
        for otherSystemName, otherInfo in identifiedSystems.items():
            if otherSystemName == systemName:
                continue
            other_elements = otherInfo.get("ElementIDs", [])
            other_ahu_elements = [el for el in other_elements if ifc_file.by_id(el).is_a("IfcUnitaryEquipment") or ('Geniox' in str(ifc_file.by_id(el).ObjectType))]
            # if any of the ahu_elements are in other_ahu_elements, consider them paired
            if any(ahu in other_ahu_elements for ahu in ahu_elements):
                pairedSystems.append(otherSystemName)
        if pairedSystems:
            identifiedSystems[systemName]['PairedSystems'] = pairedSystems


    # table of AHUs and their respective supply and return systems (with element counts)
    table_AHUs = Table(title="AHU Elements and their Systems", show_lines=True)
    table_AHUs.add_column("AHU Element GlobalId", style="cyan", no_wrap=True)
    table_AHUs.add_column('Supply System (Element Count)', style="red")
    table_AHUs.add_column('Return System (Element Count)', style="blue")


    processed_AHUs = set()
    # VI=Supply, VU=Return
    for systemName, info in identifiedSystems.items():
        elements = info.get("ElementIDs", [])
        ahu_elements = [el for el in elements if ifc_file.by_id(el).is_a("IfcUnitaryEquipment") or ('Geniox' in str(ifc_file.by_id(el).ObjectType))]
        for ahu in ahu_elements:
            if ahu in processed_AHUs:
                continue
            supplySystem = systemName if 'VI' in systemName else None
            returnSystem = systemName if 'VU' in systemName else None
            # check paired systems for the other type
            pairedSystems = info.get('PairedSystems', [])
            for pairedSystem in pairedSystems:
                if 'VI' in pairedSystem:
                    supplySystem = pairedSystem
                elif 'VU' in pairedSystem:
                    returnSystem = pairedSystem
            supplyCount = identifiedSystems[supplySystem]['ElementCount'] if supplySystem else 0
            returnCount = identifiedSystems[returnSystem]['ElementCount'] if returnSystem else 0
            table_AHUs.add_row(ahu, f"{supplySystem} ({supplyCount})" if supplySystem else 'N/A', f"{returnSystem} ({returnCount})" if returnSystem else 'N/A')
            processed_AHUs.add(ahu)

    console.print(table_AHUs)

    console.print(f"\n Number of systems WITHOUT AHU elements: [bold red]{len(missingAHUsystems)}[/bold red]\n Number of elements not analyzed: [bold red]{sum(v.get("ElementCount", 0) for v in missingAHUsystems.values())}[/bold red]\n")

    return identifiedSystems, missingAHUsystems


def get_element_bbox(element):
    """Return min/max XYZ coordinates of an IFC element in world coordinates."""
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    shape = ifcopenshell.geom.create_shape(settings, element)
    verts = np.array(shape.geometry.verts).reshape(-1, 3)

    bbox_min = verts.min(axis=0)
    bbox_max = verts.max(axis=0)

    return {"min": bbox_min, "max": bbox_max}

# new function should check all air terminals in each system, check if they clash with a space, and if so, add the required air flow to the system.
# then, check if the ducts in the system are dimensioned correctly for the required air flow    
def bbox_overlap(b1, b2):
    return all(
        b1["min"][i] <= b2["max"][i] and b1["max"][i] >= b2["min"][i]
        for i in range(3)
    )

def airTerminalSpaceClashAnalyzer(console, MEP_file_withSpaces, identifiedSystems):
    """Check which air terminals are inside which spaces.
    Returns: A dictionary with space.GlobalId as key and a list of air terminal GlobalIds as values.
    """
    spaces = MEP_file_withSpaces.by_type("IfcSpace")
    # spaces with a long name of Area should be ignored
    spaces = [space for space in spaces if 'Area' not in space.LongName]
    spaces = [space for space in spaces if 'Rooftop Terrace' not in space.LongName]

    # Precompute space bounding boxes
    space_bboxes = {}
    for space in spaces:
        try:
            bbox = get_element_bbox(space)
            space_bboxes[space.GlobalId] = {"space": space, **bbox}
        except Exception as e:
            console.print(f"[yellow]Skipping space {space.GlobalId}: {e}[/yellow]")

    spaceTerminals = {}

    for systemName, info in identifiedSystems.items():
        # console.print(f"\n[bold cyan]Analyzing system {systemName}[/bold cyan]")
        elements = info.get("ElementIDs", [])
        air_terminals = [el for el in elements if MEP_file_withSpaces.by_id(el).is_a("IfcAirTerminal")]
        # console.print(f"System {systemName}: {air_terminals}")
        for air_terminal in air_terminals:
            try:
                at_bbox = get_element_bbox(MEP_file_withSpaces.by_id(air_terminal))
            except Exception as e:
                console.print(f"[yellow]Skipping air terminal {air_terminal}: {e}[/yellow]")
                continue

            found_space = None
            for sid, sdata in space_bboxes.items():
                if bbox_overlap(at_bbox, sdata):
                    found_space = sdata["space"]
                    # console.print(f"✅ Air terminal {air_terminal} inside space {found_space.LongName}")
                    break

            if not found_space:
                # console.print(f"[bold red]❌ Air terminal {air_terminal} not inside any space[/bold red]")
                pass

            if found_space:
                if found_space.GlobalId not in spaceTerminals:
                    spaceTerminals[found_space.GlobalId] = {"Supply": [], "Return": []}
                if 'VU' in systemName:
                    spaceTerminals[found_space.GlobalId]["Return"].append(air_terminal)
                elif 'VI' in systemName:
                    spaceTerminals[found_space.GlobalId]["Supply"].append(air_terminal)

            elif not found_space: # unassigned air terminals
                if "Unassigned" not in spaceTerminals:
                    spaceTerminals["Unassigned"] = {"Supply": [], "Return": []}

                if 'VU' in systemName:
                    spaceTerminals["Unassigned"]["Return"].append(air_terminal)
                elif 'VI' in systemName:
                    spaceTerminals["Unassigned"]["Supply"].append(air_terminal)

    # create table with space names and number of air terminals in each space - lastly a row with unnassigned air terminals
    table_spaces = Table(title="Air Terminals in Spaces", show_lines=True)
    table_spaces.add_column("Space Long Name", style="green", no_wrap=True)
    table_spaces.add_column("Supply Air Terminals", style="red")
    table_spaces.add_column("Return Air Terminals", style="blue")

    for spaceID, terminals in spaceTerminals.items():
        if spaceID == "Unassigned":
            pass
        else:
            table_spaces.add_row(MEP_file_withSpaces.by_guid(spaceID).LongName, str(len(terminals.get("Supply", []))), str(len(terminals.get("Return", []))))
    
    # add unassigned row
    table_spaces.add_row("[bold red]Unassigned[/bold red]", str(len(spaceTerminals.get("Unassigned", {}).get("Supply", []))), str(len(spaceTerminals.get("Unassigned", {}).get("Return", []))))
    # console.print(table_spaces)

    return spaceTerminals

def spaceAirFlowCalculator(console, MEP_file_withSpaces, spaceTerminals):
    """Calculate required air flow for each space based on space.LongName and number of air terminals.
    Returns: A dictionary with space.GlobalId as key and required air flow as values.
    """

    # ask for user input for which category the building is (cat I, II, III, IV) - only II implemented

    # building_category = console.input("[bold blue]Enter the building category (I, II, III, IV): [/bold blue]")
    # building_category = building_category.strip().upper()
    # if building_category not in ['I', 'II', 'III', 'IV']:
    #     console.print("[bold red]Invalid building category. Defaulting to II.[/bold red]")
    #     building_category = 'II'
    # else:
    #     console.print(f"[bold green]Building category set to {building_category}.[/bold green]")

    building_category = 'II'  # default to II for now
    
    # According to DS_EN 16798-1:2019
    airFlowDict = {
        'I': {
            'l/s per person': 10,  # l/s per person
            'l/s per area': 1.0,  # l/s per m²
            'l/s backup': 2  # l/s per m² (if person density is unknown)
        },
        'II': {
            'l/s per person': 7,  # l/s per person
            'l/s per area': 0.7,  # l/s per m²
            'l/s backup': 1.4  # l/s per m² (if person density is unknown)
        },
        'III': {
            'l/s per person': 4,  # l/s per person
            'l/s per area': 0.4,  # l/s per m²
            'l/s backup': 0.8  # l/s per m² (if person density is unknown)
        },
        'IV': {
            'l/s per person': 2.5,  # l/s per person
            'l/s per area': 0.3,  # l/s per m²
            'l/s backup': 0.55  # l/s per m² (if person density is unknown)
        }
    }


    # dont know how to get person density from ifc spaces...
    assumedPersonDensityDict = { 
        'Open Office': 17,  # m² per person
        'Closed Office': 10,  # m² per person
        'Classroom': 2,  # m² per person
        'Meeting Room': 2,  # m² per person
        'Auditorium': 5,  # m² per person

        'Backup': 10  # m² per person
        }

    spaceAirFlows = {}



    # get GrossFloorArea from IfcElementQuantity for all spaces
    spaceAreas = {}
    for spaceID in spaceTerminals.keys():
        if spaceID == "Unassigned":
            continue
        else:
            spaceAreas[spaceID] = 0
            for rel in getattr(MEP_file_withSpaces.by_guid(spaceID), "IsDefinedBy", []):
                propdef = rel.RelatingPropertyDefinition
                if propdef.is_a("IfcElementQuantity"):
                    for q in propdef.Quantities:
                        if getattr(q, "Name", "") == "GrossFloorArea":
                            spaceAreas[spaceID] = getattr(q, "AreaValue", 0)
                            break
                if spaceAreas[spaceID] != 0:
                    break

    # console.print(f"GrossFloorArea: {spaceAreas}")

    # calculate required air flow per m² for each space type
    for spaceID, terminals in spaceTerminals.items():
        if spaceID == "Unassigned":
            continue

        space = MEP_file_withSpaces.by_guid(spaceID)
        area = spaceAreas.get(spaceID, 0)  # in m²
        spaceType = space.LongName

        if spaceType in assumedPersonDensityDict:
            assumedOccupancy = area / assumedPersonDensityDict[spaceType]
            requiredAirFlow = (area / assumedPersonDensityDict[spaceType]) * airFlowDict[building_category]['l/s per person'] + (area * airFlowDict[building_category]['l/s per area'])
        else:
            # use backup values
            assumedOccupancy = area / assumedPersonDensityDict['Backup']
            requiredAirFlow = (area / assumedPersonDensityDict['Backup']) * airFlowDict[building_category]['l/s backup'] + (area * airFlowDict[building_category]['l/s per area'])

        spaceAirFlows[spaceID] = {
            'SpaceLongName': spaceType,
            'Area_m2': round(area,2),
            'Assumed_Occupancy': round(assumedOccupancy, 2),
            'RequiredAirFlow_l_s': round(requiredAirFlow, 2),
            'SupplyTerminals': terminals.get("Supply", []),
            'SupplyAirFlow': round(requiredAirFlow / max(1, len(terminals.get("Supply", []))), 2) if terminals.get("Supply", []) else 0,
            'ReturnTerminals': terminals.get("Return", []),
            'ReturnAirFlow': round(requiredAirFlow / max(1, len(terminals.get("Return", []))), 2) if terminals.get("Return", []) else 0,
        }


    # table with required air flows per active space
    table_airflows = Table(title="Required Air Flows per Space", show_lines=True)
    table_airflows.add_column("Space Long Name", style="green", no_wrap=True)
    table_airflows.add_column("Area (m²)", style="cyan")
    table_airflows.add_column("Assumed Occupancy", style="cyan")
    table_airflows.add_column("Required Air Flow (l/s)", style="magenta")
    table_airflows.add_column("Supply Terminals", style="red")
    table_airflows.add_column("Supply Air Flow (l/s term.)", style="red")
    table_airflows.add_column("Return Terminals", style="blue")
    table_airflows.add_column("Return Air Flow (l/s term.)", style="blue")
    for spaceID, data in spaceAirFlows.items():
        table_airflows.add_row(
            data['SpaceLongName'],
            str(data['Area_m2']),
            str(data['Assumed_Occupancy']),
            str(data['RequiredAirFlow_l_s']),
            str(len(data['SupplyTerminals'])),
            str(data['SupplyAirFlow']),
            str(len(data['ReturnTerminals'])),
            str(data['ReturnAirFlow'])
        )
    console.print(table_airflows)


    return spaceAirFlows






# console = Console()

# ifc_file = ifcopenshell.open('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/outputFiles/ElementLeveler_withSpaces.ifc')
# identifiedSystems, missingAHUsystems = systemAnalyzer(console=console, ifc_file=ifc_file, targetSystems='IfcDistributionSystem')

# spaceTerminals = airTerminalSpaceClashAnalyzer(console=console, MEP_file_withSpaces=ifc_file, identifiedSystems=identifiedSystems)
# spaceAirFlows = spaceAirFlowCalculator(console=console, MEP_file_withSpaces=ifc_file, spaceTerminals=spaceTerminals)


