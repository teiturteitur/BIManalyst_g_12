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
import ifcopenshell

if __name__ == "__main__":


    #load the IFC file
    # ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-06-D-MEP.ifc")
    # ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-08-D-MEP.ifc")
    ifc_file = ifcopenshell.open("ifcFiles/25-16-D-MEP.ifc")
    ElementLeveler.ElementLevelChecker(ifc_file=ifc_file, elementType="IfcDuctSegment", colorQuestion=False)
    FreeHeightChecker.FreeHeightChecker(ifc_file=ifc_file, elementType='IfcDuctSegment', minFreeHeight=2.6, colorQuestion=True)
    # save the ifc file to desktop
    levelCheckFileName = "ElementLevelerTEST.ifc"
    # levelCheckedIFC.write("/Users/teiturheinesen/Desktop/" + levelCheckFileName)
    # print("Element Leveled IFC file saved to desktop as " + levelCheckFileName)
    FreeHeightFileName = "FreeHeightChecker.ifc"
    ifc_file.write("ifcFiles/" + FreeHeightFileName)
    print("Free Height IFC file saved to desktop as " + FreeHeightFileName)


    print("Done!")
