########################################################
"""
ELEMENT LEVELER + FREE HEIGHT CHECKER

Version: 27/10/2025

The following script
and checks if it is defined on the correct level in the IFC file.

How to use:
- Load your IFC file by uploading it to the "ifcFiles" folder
    - IMPORTANT: If the MEP file (XXXX-MEP.ifc) does not contain spaces, also upload the corresponding ARCH (XXXX-ARCH.ifc) file containing the spaces
- Run main.py and follow the instructions in the CLI

Future Work:
    small(er) stuff

    - MAYBE? I DONT KNOW IF THIS IS BETTER:
    check if bounding box function should be something like ifcopenshell.util.shape.get_bbox(element) instead of creating geometry each time
    maybe its better to use ifcopenshell trees?

    - find a way to check orientation of elements (make vectors from ports!!)

    - make sure that elements are geometrically connected and not just connected by ports

    - make sure that elements are assigned to the same system if they are connected

    - convert sanity checks to IDS? https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/

    - send notification/email to responsible person when elements in BCF file are assigned to them (IFCPERSON)?

    big stuff

    - find ifc____profiledef for ducts to get dimensions of ducts. i.e. ifccircularprofiledef, ifcrectangleprofiledef, etc.

    - make sure each element is dimensioned according to pressure losses and required air flows


Authors: s214310, s203493, s201348

"""
########################################################

from scripts import ElementLeveler
from scripts import FreeHeightChecker
from scripts import setupFunctions
from scripts import systemAnalyzer
import os
from datetime import datetime
import ifcopenshell
from rich.console import Console
from rich.spinner import Spinner
from rich.prompt import Prompt
from rich.panel import Panel

if __name__ == "__main__":
    start_time = datetime.now()
    console = Console()
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold magenta]⭐ IFC HVAC SYSTEM ANALYZER + FREEHEIGHTCHECKER ⭐[/bold magenta]\n\n[green]Advanced BIM - E25[/green]",
            title="[bold yellow]BIManalyst TOOL[/bold yellow]",
            subtitle="by Group 12",
            border_style="cyan",
        )
    )

    # ask user to choose IFC file pair from directory
    ifc_fileName, ifc_SpaceFile = setupFunctions.choose_ifc_pair_from_directory(
        console, "ifcFiles", extension=".ifc"
    )
    ifc_file = ifcopenshell.open(ifc_fileName)
    ifc_file_Spaces = ifcopenshell.open(ifc_SpaceFile)

    # define target elements
    targetElements = setupFunctions.choose_ifcElementType(
        console, ifcFile=ifc_file, category="MEP-HVAC"
    )

    # Check element placements in the IFC file
    with console.status(
        "\n[bold green]Checking element placements in the IFC file...", spinner="dots"
    ):
        ifc_file_levelChecked, misplacedElements = ElementLeveler.ElementLevelChecker(
            console=console, ifc_file=ifc_file, targetElements=targetElements
        )

    # Analyze building systems
    with console.status(
        "\n[bold green]Analyzing building systems in the IFC file...", spinner="dots"
    ):
        identifiedSystems, missingAHUsystems = systemAnalyzer.systemAnalyzer(
            console=console,
            ifc_file=ifc_file_levelChecked,
            targetSystems="IfcDistributionSystem",
        )

    # Check what air terminals are in which spaces
    with console.status(
        "\n[bold green]Checking air terminal placements in spaces...", spinner="dots"
    ):
        spaceTerminals, unassignedTerminals = (
            systemAnalyzer.airTerminalSpaceClashAnalyzer(
                console=console,
                MEP_file=ifc_file_levelChecked,
                space_file=ifc_file_Spaces,
                space_file_name="ARCH FILE",
                identifiedSystems=identifiedSystems,
            )
        )

    # Calculate required air flows for each air terminal (located in a space)
    with console.status(
        "\n[bold green]Calculating required air flows for spaces...", spinner="dots"
    ):
        spaceAirFlows = systemAnalyzer.spaceAirFlowCalculator(
            console=console,
            MEP_file=ifc_file_levelChecked,
            space_file=ifc_file_Spaces,
            spaceTerminals=spaceTerminals,
            unassignedTerminals=unassignedTerminals,
        )

    # with console.status("[bold green]Checking free heights in the (corrected) IFC file...", spinner='dots'):
    #     ifc_fileFHC = FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_fileELC, targetElements=targetElements, minFreeHeight=2.6, colorQuestion=False)
    #     # save the ifc file to desktop
    #     FreeHeightFileName = "FreeHeightChecker.ifc"
    #     ifc_fileFHC.write("outputFiles/" + FreeHeightFileName)
    # console.print("Free Height IFC file saved as " + FreeHeightFileName)

    # ask if user wants to display system tree structure
    while True:
        showChoice = (
            Prompt.ask("\n Do you want to display the system tree structure? [y/n]")
            .strip()
            .lower()
        )
        if showChoice not in ["y", "n"]:
            console.print("[red]Invalid choice. Please enter 'y' or 'n'.[/red]")
        else:
            break

    with console.status(
        "\n[bold green]Calculating required air flows for spaces...", spinner="dots"
    ):
        systemsTree = systemAnalyzer.findSystemTrees(
            console=console,
            identifiedSystems=identifiedSystems,
            ifc_file=ifc_file_levelChecked,
            spaceAirFlows=spaceAirFlows,
            showChoice=showChoice,
        )

    with console.status(
        "\n[bold green]Generating BCF file with issues found...", spinner="dots"
    ):
        setupFunctions.generate_bcf_from_errors(
            console=console,
            ifc_file=ifc_file_levelChecked,
            ifc_file_path=ifc_fileName,
            misplacedElements=misplacedElements,
            missingAHUsystems=missingAHUsystems,
            unassignedTerminals=unassignedTerminals,
            output_bcf="outputFiles/hvacReport.bcfzip",
        )

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    console.print(
        f"\n[bold cyan]Done!\nElapsed time: {round(elapsed_time.total_seconds(), 2)} seconds[/bold cyan]\n"
    )
