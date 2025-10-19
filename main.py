########################################################
'''
ELEMENT LEVELER + FREE HEIGHT CHECKER

Version: 22/09/2025

The following script takes an element type as input (e.g. IfcDuctSegment) 
and checks if it is defined on the correct level in the IFC file. 

How to use:
- Load your IFC file by changing the path for the ifc_file variable
- Run main.py and follow the instructions in the CLI


Future Work:
    small(er) stuff
    - BCF files instead of text files

    - Pick entire systems instead of element types (e.g. the whole duct system including fittings and air terminals)

    - create simple UI or pop-up window to select the IFC file and element type 

    - send notification/email to responsible person when elements in BCF file are assigned to them (IFCPERSON)

    
    big stuff
    - Import spaces from ARCH IFC model and do clash detection with MEP elements to determine placements of elements

    - check ifcopenshell.IfcDistributionElement.HasPorts to make sure that all elements are connected

    - for each space, calculate the required air flow according to space type/usage etc.

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

    console = Console()
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]⭐ IFC ELEMENTLEVELER + FREEHEIGHTCHECKER ⭐[/bold magenta]\n\n[green]Advanced BIM - E25[/green]",
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

    ########################################################
    #                   TOOL STARTS HERE                   #
    ########################################################
    

    # Check element placements in the IFC file
    with console.status("\n[bold green]Checking element placements in the IFC file...", spinner='dots'):
        ifc_file_levelChecked, misplacedElements = ElementLeveler.ElementLevelChecker(console=console, ifc_file=ifc_file, targetElements=targetElements, colorQuestion=False)


    # Analyze building systems
    with console.status("\n[bold green]Analyzing building systems in the IFC file...", spinner='dots'):
        identifiedSystems, missingAHUsystems = systemAnalyzer.systemAnalyzer(console=console, ifc_file=ifc_file_levelChecked, targetSystems='IfcDistributionSystem')


    # merge spaces into the mep ifc file
    if not ifc_file_levelChecked.by_type("IfcSpace"):
        with console.status("\n[bold green]Merging spaces into the MEP IFC file...", spinner='dots'):
            ifc_file_withSpaces, newSpaces = setupFunctions.merge_spaces_with_quantities_and_structure(console=console, source_ifc=ifc_file_Spaces, target_ifc=ifc_file_levelChecked)

            # save the ifc file with spaces to outputFiles
            levelCheckFileName = "ElementLeveler_withSpaces.ifc"
            ifc_file_withSpaces.write("outputFiles/" + levelCheckFileName)
            # console.print("Element Leveler IFC file with Spaces saved as " + levelCheckFileName)

    with console.status("\n[bold green]Checking air terminal placements in spaces...", spinner='dots'):
        spaceTerminals, unassignedTerminals = systemAnalyzer.airTerminalSpaceClashAnalyzer(console=console, MEP_file_withSpaces=ifc_file_withSpaces, identifiedSystems=identifiedSystems)



    with console.status("\n[bold green]Calculating required air flows for spaces...", spinner='dots'):
        spaceAirFlows = systemAnalyzer.spaceAirFlowCalculator(console=console, MEP_file_withSpaces=ifc_file_withSpaces, spaceTerminals=spaceTerminals)

    # console.print(f'\n {misplacedElements=} \n {missingAHUsystems=} \n {unassignedTerminals=}')

    # with console.status("[bold green]Checking free heights in the (corrected) IFC file...", spinner='dots'):
    #     ifc_fileFHC = FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_fileELC, targetElements=targetElements, minFreeHeight=2.6, colorQuestion=False)
    #     # save the ifc file to desktop
    #     FreeHeightFileName = "FreeHeightChecker.ifc"
    #     ifc_fileFHC.write("outputFiles/" + FreeHeightFileName)
    #     console.print("Free Height IFC file saved as " + FreeHeightFileName)

    # setupFunctions.writeBCF(console=console, misplacedElements=misplacedElements, missingAHUsystems=missingAHUsystems, unassignedTerminals=unassignedTerminals)
    
    with console.status("\n[bold green]Generating BCF file with issues found...", spinner='dots'):
        setupFunctions.generate_bcf_from_errors(console=console, ifc_file=ifc_file_withSpaces,
                                                misplacedElements=misplacedElements,
                                                missingAHUsystems=missingAHUsystems,
                                                unassignedTerminals=unassignedTerminals,
                                                output_bcf="outputFiles/hvacReport.bcfzip")


    console.print("[bold cyan]Done![bold cyan]\n")
