########################################################
"""
AIR FLOW ESTIMATOR / VENTILATION SYSTEM ANALYZER / BCF GENERATOR

Version: 21/11/25

The following project consists of three modules.

01_AirFlowEstimator
    Input:
        ARCH.ifc file.
            An architectural ifc file containing spaces (uploaded to /IfcFiles)

    Output:
        spaceAirFlows: dict{ifcopenshell.entity_instance: float}
                Dictionary with spaces in ARCH file and corresponding estimation of air flows (l/s).

02_VentilationSystemAnalyzer
    Input:
        MEP.ifc file.
            A MEP IFC file containing ventilation systems.

        spaceAirFlows.
            See 01_AirFlowEstimator

    Output:
        Dictionary of elements that have failed the performed checks.

        Report of analyzed ventilation system (in terminal).

03_BcfGenerator
    Input:
        Dictionary of elements and their corresponding errors.

    Output:
        BcfXML file.


How to use:
- Load your IFC file by uploading it to the "ifcFiles" folder
    - IMPORTANT: TWO FILES ARE NEEDED!
        - One xxx_MEP.ifc file containing the ventilation systems
        - One xxx_ARCH.ifc file containing spaces (and furniture for occupancy estimation)
- Run main.py and follow the instructions in the CLI
- Enjoy BCF files of failing checks and terminal output :)

Future Work:
    small(er) stuff

    - make sure that elements are geometrically connected and not just connected by ports

    - convert sanity checks to IDS? https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/

    - send notification/email to responsible person when elements in BCF file are assigned to them (IFCPERSON)?

    big stuff

    - make sure each element is dimensioned according to pressure losses and required air flows


Authors: s214310, s203493, s201348

"""
########################################################

from scripts import ElementLeveler
from scripts import FreeHeightChecker

from AirflowEstimator.AirFlowEstimator import spaceAirFlowCalculator
from VentilationSystemAnalyzer.VentilationSystemAnalyzer import *
from BcfGenerator.BcfGenerator import *

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
    ifc_filePath, ifc_SpacePath = setupFunctions.choose_ifc_pair_from_directory(
        console=console, directory="A3/ifcFiles", extension=".ifc"
    )
    ifc_file = ifcopenshell.open(ifc_filePath)
    space_file_beforeCheck = ifcopenshell.open(ifc_SpacePath)
    ifc_file_Spaces = spaceAirFlowCalculator(
        console=console, space_file=space_file_beforeCheck
    )

    # define target elements
    targetElements = setupFunctions.choose_ifcElementType(
        console=console, ifcFile=ifc_file, category="MEP-HVAC"
    )

    with console.status(status = 'Finding ventilation systems with AHUs...', spinner = 'dots'):
        identifiedSystems, missingAHUsystems, table_AHUs = ahuFinder(
            console=console, ifc_file=ifc_file, targetSystems="IfcDistributionSystem"
        )

    with console.status(status = 'Connecting air terminals with spaces...', spinner='dots'):
        spaceTerminals, unassignedTerminals, table_Spaces = airTerminalSpaceClashAnalyzer(
            console=console,
            MEP_file=ifc_file,
            space_file=ifc_file_Spaces,
            identifiedSystems=identifiedSystems,
            space_file_name="25-10-D-ARCH.ifc",
        )

    with console.status(status='Assigning air flows and pressure losses to air terminals...'):
        systemsTree, ifc_file_new = getSystemTrees(
            console=console,
            identifiedSystems=identifiedSystems,
            ifc_file=ifc_file,
            space_file=ifc_file_Spaces,
            spaceTerminals=spaceTerminals,
            showChoice="n",
        )


    with console.status(status='Generating BCF-file...', spinner='dots'):
        old_generate_bcf_from_errors(console=console, ifc_file=ifc_file, ifc_file_path=ifc_filePath, missingAHUsystems=missingAHUsystems,
                                     unassignedTerminals=unassignedTerminals, output_bcf='A3/outputFiles/HVAC_Issues.bcfzip')

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    console.print(
        f"\n[bold cyan]Done!\nElapsed time: {round(elapsed_time.total_seconds(), 2)} seconds[/bold cyan]\n"
    )
