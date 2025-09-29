########################################################
'''
ELEMENT LEVELER + FREE HEIGHT CHECKER

Version: 22/09/2025

The following script takes an element type as input (e.g. IfcDuctSegment) 
and checks if it is defined on the correct level in the IFC file. 

How to use:
- Load your IFC file by changing the path for the ifc_file variable
- Specify the element type you want to check (currently set to IfcDuctSegment)
- Run main.py


Future Work:
- Counter of moved elements and elements with insufficient free height
- General statistics report
- GUI?


Authors: s214310, s203493, s201348

'''
########################################################

from scripts import ElementLeveler 
from scripts import FreeHeightChecker
import os
from datetime import datetime
import ifcopenshell
from rich.console import Console
from rich.spinner import Spinner

if __name__ == "__main__":

    #load the IFC file
    ifc_fileName = "25-16-D-MEP.ifc" # CHANGE THIS TO YOUR IFC FILE NAME!


    console = Console()
    # ask for what should be checked
    elementType = console.input("Please select which element type should be checked (default is IfcDuctSegment): [bold green](IfcDuctSegment/IfcPipeSegment/IfcBeam)[/bold green] ") or "IfcDuctSegment"

    # ask if a new ElementLevelChecker.ifc should be saved
    ELCcolorQuestion = console.input("Do you want a new IFC file, where potentially misplaced elements are colored? [bold green](y/n)[/bold green] ") or "y"
    if ELCcolorQuestion.lower() == 'y':
        ELCcolorQuestion = True
    else:
        ELCcolorQuestion = False

    # ask if a new FreeHeightChecker.ifc should be saved
    FHCcolorQuestion = console.input("Do you want a new IFC file, where the lowest element on each level is colored? [bold green](y/n)[/bold green] ") or "y"
    if FHCcolorQuestion.lower() == 'y':
        FHCcolorQuestion = True
    else:
        FHCcolorQuestion = False

    ########################################################
    #                   TOOL STARTS HERE                   #
    ########################################################
    
    ifc_file = ifcopenshell.open(f"ifcFiles/{ifc_fileName}")

    # Check element placements in the IFC file
    with console.status("[bold green]Checking element placements in the IFC file...", spinner='dots'):
        ifc_fileELC, misplacedElements = ElementLeveler.ElementLevelChecker(ifc_file=ifc_file, elementType=elementType, colorQuestion=ELCcolorQuestion)
    console.print(f"Total elements potentially misplaced: {len(misplacedElements[0]) + len(misplacedElements[1])} \n")
    if ELCcolorQuestion is True:
        # save the ifc file to desktop
        levelCheckFileName = "ElementLeveler.ifc"
        ifc_fileELC.write("ifcFiles/" + levelCheckFileName)
        console.print("Element Leveler IFC file saved as " + levelCheckFileName)

    # Check free heights in the corrected IFC file
    with console.status("[bold green]Checking free heights in the (corrected) IFC file...", spinner='dots'):
        ifc_fileFHC = FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_fileELC, elementType='IfcDuctSegment', minFreeHeight=2.6, colorQuestion=True)

    if FHCcolorQuestion is True:
        # save the ifc file to desktop
        FreeHeightFileName = "FreeHeightChecker.ifc"
        ifc_fileFHC.write("ifcFiles/" + FreeHeightFileName)
        console.print("Free Height IFC file saved as " + FreeHeightFileName)


    # write misplacedElements into text file
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")
    with open(f"ifcFiles/misplacedElements_REPORT_{dt_string}.txt", "w") as f:
        f.write(f"Misplaced Elements Report - Generated on {dt_string}\n")
        f.write("========================================\n\n")
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
    




    console.print("Done!")
