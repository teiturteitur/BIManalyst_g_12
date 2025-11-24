import ifcopenshell
import rich
from rich.console import Console
from ..scripts.setupFunctions import *



def menuFilePicker(console):

# ask user to choose IFC file pair from directory
    ifc_filePath, ifc_SpacePath = setupFunctions.choose_ifc_pair_from_directory(
        console=console, directory="A3/ifcFiles", extension=".ifc"
    )
    ifc_file = ifcopenshell.open(ifc_filePath)
    space_file_beforeCheck = ifcopenshell.open(ifc_SpacePath)
    
    # define target elements
    targetElements = setupFunctions.choose_ifcElementType(
        console=console, ifcFile=ifc_file, category="MEP-HVAC"
    )
    return ifc_filePath, ifc_file, space_file_beforeCheck, ifc_file_Spaces, targetElements

def menuIFCAnalysis(console: Console, MEP_file: ifcopenshell.file | None, Space_file: ifcopenshell.file):
    
    ifc_file_Spaces = spaceAirFlowCalculator(
        console=console, space_file=space_file_beforeCheck
    )

    if MEP_file:
        


