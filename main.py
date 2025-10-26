########################################################
'''
ELEMENT LEVELER + FREE HEIGHT CHECKER

Version: 22/09/2025

The following script 
and checks if it is defined on the correct level in the IFC file. 

How to use:
- Load your IFC file by uploading it to the "ifcFiles" folder
    - IMPORTANT: If the MEP file (XXXX-MEP.ifc) does not contain spaces, also upload the corresponding ARCH (XXXX-ARCH.ifc) file containing the spaces
- Run main.py and follow the instructions in the CLI

Future Work:
    small(er) stuff
    - MAYBE? I DONT KNOW IF THIS IS BETTER: 
    change bounding box function to use ifcopenshell.util.shape.get_bbox(element) instead of creating geometry each time
    
    - send notification/email to responsible person when elements in BCF file are assigned to them (IFCPERSON)?

    big stuff
    
    - convert CLI to TUI (using textual instead of Rich)

    - if a space contains air terminals, divide the required air flow between them and do the following:
        - for each air terminal in each space, check connected duct/fitting and add the required air flow to it
        - continue upstream until the main duct is reached (until the duct ends)
        - when all air terminals have been processed, check if the ducts are correctly dimensioned for the required air flow
        - if not, make a suggestion in the bcf file


Authors: s214310, s203493, s201348

'''
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
from rich.panel import Panel

if __name__ == "__main__":

    start_time = datetime.now()
    console = Console()
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]⭐ IFC HVAC SYSTEM ANALYZER + FREEHEIGHTCHECKER ⭐[/bold magenta]\n\n[green]Advanced BIM - E25[/green]",
        title="[bold yellow]BIManalyst TOOL[/bold yellow]",
        subtitle="by Group 12",
        border_style="cyan"
    ))
    
    # ask user to choose IFC file pair from directory
    ifc_fileName, ifc_SpaceFile = setupFunctions.choose_ifc_pair_from_directory(console, "ifcFiles", extension=".ifc")
    ifc_file = ifcopenshell.open(ifc_fileName)
    ifc_file_Spaces = ifcopenshell.open(ifc_SpaceFile)

    # define target elements
    targetElements = setupFunctions.choose_ifcElementType(console, ifcFile=ifc_file, category='MEP-HVAC')

    # Check element placements in the IFC file
    with console.status("\n[bold green]Checking element placements in the IFC file...", spinner='dots'):
        ifc_file_levelChecked, misplacedElements = ElementLeveler.ElementLevelChecker(console=console, ifc_file=ifc_file, targetElements=targetElements, colorQuestion=False)

    # Analyze building systems
    with console.status("\n[bold green]Analyzing building systems in the IFC file...", spinner='dots'):
        identifiedSystems, missingAHUsystems = systemAnalyzer.systemAnalyzer(console=console, ifc_file=ifc_file_levelChecked, targetSystems='IfcDistributionSystem')

    # Check what air terminals are in which spaces
    with console.status("\n[bold green]Checking air terminal placements in spaces...", spinner='dots'):
        spaceTerminals, unassignedTerminals = systemAnalyzer.airTerminalSpaceClashAnalyzer(console=console, MEP_file=ifc_file_levelChecked, space_file=ifc_file_Spaces, space_file_name='ARCH FILE', identifiedSystems=identifiedSystems)

    # Calculate required air flows for each air terminal (located in a space)
    with console.status("\n[bold green]Calculating required air flows for spaces...", spinner='dots'):
        spaceAirFlows = systemAnalyzer.spaceAirFlowCalculator(console=console, MEP_file=ifc_file_levelChecked, space_file=ifc_file_Spaces, spaceTerminals=spaceTerminals, unassignedTerminals=unassignedTerminals)


    # with console.status("[bold green]Checking free heights in the (corrected) IFC file...", spinner='dots'):
    #     ifc_fileFHC = FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_fileELC, targetElements=targetElements, minFreeHeight=2.6, colorQuestion=False)
    #     # save the ifc file to desktop
    #     FreeHeightFileName = "FreeHeightChecker.ifc"
    #     ifc_fileFHC.write("outputFiles/" + FreeHeightFileName)
    #     console.print("Free Height IFC file saved as " + FreeHeightFileName)

    with console.status("\n[bold green]Generating BCF file with issues found...", spinner='dots'):
        setupFunctions.generate_bcf_from_errors(console=console, ifc_file=ifc_file_levelChecked,
                                                ifc_file_path=ifc_fileName,
                                                misplacedElements=misplacedElements,
                                                missingAHUsystems=missingAHUsystems,
                                                unassignedTerminals=unassignedTerminals,
                                                output_bcf="outputFiles/hvacReport.bcfzip")


    end_time = datetime.now()
    elapsed_time = end_time - start_time
    console.print(f"\n[bold cyan]Done!\nElapsed time: {round(elapsed_time.total_seconds(),2)} seconds[/bold cyan]\n")
