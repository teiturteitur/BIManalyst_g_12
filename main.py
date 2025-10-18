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
from scripts import menuFunctions
import os
from datetime import datetime
import ifcopenshell
from rich.console import Console
from rich.spinner import Spinner
from rich.panel import Panel

if __name__ == "__main__":

    #load the IFC file
  

    console = Console()
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]⭐ IFC ELEMENTLEVELER + FREEHEIGHTCHECKER ⭐[/bold magenta]\n\n[green]Advanced BIM - E25[/green]",
        title="[bold yellow]BIManalyst TOOL[/bold yellow]",
        subtitle="by Group 12",
        border_style="cyan"
    ))
    

    ifc_fileName = menuFunctions.choose_file_from_directory(console, "ifcFiles", ".ifc")

    console.print("\nTo properly run this script, a second IFC file with defined spaces is needed. (e.g. architectural model):")
    ifc_SpaceFile = menuFunctions.choose_file_from_directory(console, "ifcFiles", ".ifc", exceptions=[ifc_fileName])


    # ask for what should be checked
    elementType = console.input("\n\nPlease select which element type should be checked (default is IfcDuctSegment): [bold green](IfcDuctSegment/IfcPipeSegment etc.)[/bold green] ") or "IfcDuctSegment"

    # ask if a new ElementLevelChecker.ifc should be saved
    ELCcolorQuestion = console.input("\nDo you want a new IFC file, where potentially misplaced elements are colored? (default is yes) [bold green](y/n)[/bold green] ") or "y"
    if ELCcolorQuestion.lower() == 'y':
        ELCcolorQuestion = True
    else:
        ELCcolorQuestion = False

    # ask if a new FreeHeightChecker.ifc should be saved
    FHCcolorQuestion = console.input("\nDo you want a new IFC file, where the lowest element on each level is colored? (default is yes) [bold green](y/n)[/bold green]") or "y"
    if FHCcolorQuestion.lower() == 'y':
        FHCcolorQuestion = True
    else:
        FHCcolorQuestion = False
    
    ########################################################
    #                   TOOL STARTS HERE                   #
    ########################################################
    
    ifc_file = ifcopenshell.open(f"ifcFiles/{ifc_fileName}")

    # Check element placements in the IFC file
    with console.status("\n[bold green]Checking element placements in the IFC file...", spinner='dots'):
        ifc_fileELC, misplacedElements = ElementLeveler.ElementLevelChecker(ifc_file=ifc_file, elementType=elementType, colorQuestion=ELCcolorQuestion)
    console.print(f"""\nTotal elements potentially misplaced: {len(misplacedElements[0]) + len(misplacedElements[1])} \n
- Elements potentially placed on the wrong level: {len(misplacedElements[0])} \n
- Elements placed between levels (Should potentially be moved to building): {len(misplacedElements[1])} \n""")
    if ELCcolorQuestion is True:
        # save the ifc file to desktop
        levelCheckFileName = "ElementLeveler.ifc"
        ifc_fileELC.write("outputFiles/" + levelCheckFileName)
        console.print("Element Leveler IFC file saved as " + levelCheckFileName)

    # Check free heights in the corrected IFC file
    with console.status("[bold green]Checking free heights in the (corrected) IFC file...", spinner='dots'):
        ifc_fileFHC = FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_fileELC, elementType='IfcDuctSegment', minFreeHeight=2.6, colorQuestion=True)

    if FHCcolorQuestion is True:
        # save the ifc file to desktop
        FreeHeightFileName = "FreeHeightChecker.ifc"
        ifc_fileFHC.write("outputFiles/" + FreeHeightFileName)
        console.print("Free Height IFC file saved as " + FreeHeightFileName)


    # write misplacedElements into text file
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")
    with open(f"outputFiles/misplacedElements_REPORT_{dt_string}.txt", "w") as f:
        f.write(f"Misplaced Elements Report - Generated on {dt_string}\n")
        f.write("========================================\n")
        f.write(f"""\n Overview of potentially misplaced elements for element type: {elementType}\n
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
    




    console.print("[bold cyan]Done![bold cyan]\n")
