import ifcopenshell
from ifcopenshell.ifcopenshell_wrapper import IfcSpfHeader, Representation
import ifcopenshell.util.system

import ifcopenshell.util.pset
import ifcopenshell.util.element
import ifcopenshell.api.pset

from rich.console import Console

from rich.table import Table

from rich import inspect
import numpy as np


def spaceAirFlowCalculator(
    console: Console,
    space_file: ifcopenshell.file,
):
    """
    AIR FLOW ESTIMATOR

    Version: 17/11/25

    This tool takes architectural IFC-files (files containing spaces and possibly furniture) and estimates the required air flow needed to comply with the IEQ categories from DS_EN 16798-1:2019.

    Returns:
        airFlowFile: ifcopenshell.file
            New copy of the architectural IFC file with assigned Psets.
            If the file already contains spaces with defined Pset_SpaceOccupancyRequirements and Pset_SpaceAirHandlingDimensioning, the original file is returned.


    Author: s201348

    """

    # ask for user input for which category the building is (cat I, II, III, IV)
    building_category = console.input(
        "[bold blue]Enter the building category (I, II, III, IV): [/bold blue]"
    )
    building_category = building_category.strip().upper()
    if building_category not in ["I", "II", "III", "IV"]:
        console.print(
            "[bold red]Invalid building category. Defaulting to II.[/bold red]"
        )
        building_category = "II"
    else:
        console.print(
            f"[bold green]Building category set to {building_category}.[/bold green]"
        )

    # building_category = "II"  # default if needed

    # According to DS_EN 16798-1:2019
    airFlowDict = {
        "I": {
            "l/s per person": 10,  # l/s per person
            "l/s per area": 1.0,  # l/s per m²
            "l/s backup": 2,  # l/s per m² (if person density is unknown)
        },
        "II": {
            "l/s per person": 7,  # l/s per person
            "l/s per area": 0.7,  # l/s per m²
            "l/s backup": 1.4,  # l/s per m² (if person density is unknown)
        },
        "III": {
            "l/s per person": 4,  # l/s per person
            "l/s per area": 0.4,  # l/s per m²
            "l/s backup": 0.8,  # l/s per m² (if person density is unknown)
        },
        "IV": {
            "l/s per person": 2.5,  # l/s per person
            "l/s per area": 0.3,  # l/s per m²
            "l/s backup": 0.55,  # l/s per m² (if person density is unknown)
        },
    }
    # backup person densities, if person density is unknown. (From DS_EN 16798-1:2019 Appendix B)
    assumedPersonDensityDict = {
        "Open Office": 17,  # m² per person
        "Closed Office": 10,  # m² per person
        "Classroom": 2,  # m² per person
        "Meeting Room": 2,  # m² per person
        "Auditorium": 5,  # m² per person
        "Backup": 10,  # m² per person
    }

    allSpaces = space_file.by_type("IfcSpace")

    for space in allSpaces:
        # first, check if the pset is already defined.
        for rel in getattr(space, "IsDefinedBy", []):
            if rel.RelatingPropertyDefinition.Name in [
                "Pset_SpaceOccupancyRequirements",
                "Pset_SpaceAirHandlingDimensioning",
            ]:
                pass

        occupancyPset = ifcopenshell.api.pset.add_pset(
            file=space_file,
            product=space,
            name="Pset_SpaceOccupancyRequirements",
        )
        airFlowPset = ifcopenshell.api.pset.add_pset(
            file=space_file,
            product=space,
            name="Pset_SpaceAirHandlingDimensioning",
        )

        spaceType = space.LongName

        area = ifcopenshell.util.element.get_pset(
            element=space, name="Qto_SpaceBaseQuantities", prop="GrossFloorArea"
        )

        spaceElements = space.ContainsElements
        elementsInSpace = [
            spaceElements[element].RelatedElements
            for element in range(len(spaceElements))
        ]
        if elementsInSpace:
            assumedOccupancy = len(
                [
                    el
                    for el in elementsInSpace[0]
                    if el.is_a("IfcFurniture") and "Chair" in el.Name
                ]
            )
        else:
            assumedOccupancy = 0
        # console.print(f'{len(chairsInSpace)=} in space {space_file.by_id(spaceID).LongName}')

        if assumedOccupancy > 0:
            requiredAirFlow = (
                airFlowDict[building_category]["l/s per person"] * assumedOccupancy
            ) + (airFlowDict[building_category]["l/s per area"] * area)

            ifcopenshell.api.pset.edit_pset(
                file=space_file,
                pset=occupancyPset,
                properties={"OccupancyNumber": assumedOccupancy},
            )

            ifcopenshell.api.pset.edit_pset(
                file=space_file,
                pset=airFlowPset,
                properties={"DesignAirFlow": round(requiredAirFlow, 2)},
            )
            pass

        elif assumedOccupancy == 0:
            # console.print(f"[yellow]No chairs found in space {space.id()}[/yellow]")
            if spaceType in assumedPersonDensityDict:
                assumedOccupancy = round(
                    area / assumedPersonDensityDict[spaceType],
                    2,
                )
                requiredAirFlow = (
                    area / assumedPersonDensityDict[spaceType]
                ) * airFlowDict[building_category]["l/s per person"] + (
                    area * airFlowDict[building_category]["l/s per area"]
                )

            else:
                # use backup values
                assumedOccupancy = round(
                    area / assumedPersonDensityDict["Backup"],
                    2,
                )
                requiredAirFlow = (
                    area / assumedPersonDensityDict["Backup"]
                ) * airFlowDict[building_category]["l/s backup"] + (
                    area * airFlowDict[building_category]["l/s per area"]
                )

            ifcopenshell.api.pset.edit_pset(
                file=space_file,
                pset=occupancyPset,
                properties={"OccupancyNumber": float(assumedOccupancy)},
            )

            ifcopenshell.api.pset.edit_pset(
                file=space_file,
                pset=airFlowPset,
                properties={"DesignAirFlow": round(requiredAirFlow, 2)},
            )

        else:
            raise ValueError(f"Invalid assumed occupancy: {assumedOccupancy}")

    # table with required air flows per active space
    table_airflows = Table(title="Required Air Flows per Space", show_lines=True)
    table_airflows.add_column("Space Long Name", style="green", no_wrap=True)
    table_airflows.add_column("Global ID", style="blue")
    table_airflows.add_column("Area (m²)", style="cyan")
    table_airflows.add_column("Assumed Occupancy", style="cyan")
    table_airflows.add_column("Required Air Flow (l/s)", style="magenta")
    # table_airflows.add_column("Supply Terminals", style="red")
    # table_airflows.add_column("Supply Air Flow (l/s term.)", style="red")
    # table_airflows.add_column("Return Terminals", style="blue")
    # table_airflows.add_column("Return Air Flow (l/s term.)", style="blue")
    for space in allSpaces:
        table_airflows.add_row(
            space.LongName,
            str(space.id()),
            str(
                round(
                    ifcopenshell.util.element.get_pset(
                        element=space,
                        name="Qto_SpaceBaseQuantities",
                        prop="GrossFloorArea",
                    ),
                    2,
                )
            ),
            str(
                ifcopenshell.util.element.get_pset(
                    element=space,
                    name="Pset_SpaceOccupancyRequirements",
                    psets_only=True,
                    prop="OccupancyNumber",
                )
            ),
            str(
                ifcopenshell.util.element.get_pset(
                    element=space,
                    name="Pset_SpaceAirHandlingDimensioning",
                    prop="DesignAirFlow",
                    psets_only=True,
                )
            ),
        )
    # for spaceID, data in spaceAirFlows.items():
    #     table_airflows.add_row(
    #         data["SpaceLongName"],
    #         str(spaceID),
    #         str(data["Area_m2"]),
    #         str(data["Assumed_Occupancy"]),
    #         str(data["RequiredAirFlow_l_s"]),
    #         # str(len(data["SupplyTerminals"])),
    #         # str(data["SupplyAirFlow"]),
    #         # str(len(data["ReturnTerminals"])),
    #         # str(data["ReturnAirFlow"]),
    #     )

    # if unassignedTerminals:
    #     table_airflows.add_row(
    #         "[bold red]Unassigned[/bold red]",
    #         "-",
    #         "-",
    #         "-",
    #         str(len(unassignedTerminals.get("Supply", []))),
    #         "-",
    #         str(len(unassignedTerminals.get("Return", []))),
    #         "-",
    #     )

    console.print(table_airflows)

    return space_file


# console = Console()
# spaceFile = ifcopenshell.open(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/A3/ifcFiles/25-10-D-ARCH.ifc"
# )
# inspect(spaceFile)
# new_spaceFile = spaceAirFlowCalculator(console=console, space_file=spaceFile)
# new_spaceFile.write(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/A3/outputFiles/new_25-10-D-ARCH.ifc"
# )
