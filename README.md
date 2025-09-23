# BIManalyst group 12

FOCUS AREA: INDOOR AND ENERGY

The claim we are checking:

CHECKING FREE HEIGHTS OF ALL STOREYS

CLAIM: Ceiling heights of at least 2.6m
REPORT: D_ClientReport_Team16
PAGE: 7

TOOL DESCRIPTION:

Our tool is divided into two parts. 
- A sanity check _(scripts/ElementLevelChanger.py)_, that makes sure, that all elements are assignet to the correct level.
- A free height checker _(_scripts/FreeHeightChecker.py)_, for these elements, analyzing the vertical distance between the lowest elements lowest part and the assigned level. 

  ElementLevelChanger.py:

A sanity check is performed before analysing the free heights: All elements are checked if they are assigned to the same level as defined. Vertical elements are assigned to the building and not levels.

Output: A new IFC file, with corrected element representation. Optionally, these elements can be colored in the new IFC file, if specified.

If the elements are not in the correct level, they are moved and assigned to the correct level. If the vertical elements are assigned to a level, they are moved and assigned to the building.

  FreeHeightChecker.py:

Our script analyzes the free heights (distance from level to lowest point of ducts/air terminals) of all floors/levels in the IFC model.

Output: an overview and a new IFC file with the lowest elements on each floor colored in red.

HOW TO USE:
  - Open main.py :)
  - Load your IFC file by changing the path for the ifc_file variable
  - Specify the element type you want to check (currently set to IfcDuctSegment)
  - Run main.py


Future Work:
  - Counter of moved elements and elements with insufficient free height
  - General statistics report
  - GUI?

RESULTS:

Found Free Heights for 25-16-D-MEP.ifc:

Level 0: 2.62 m (Level: 0.0 m)

Level 1: 2.62 m (Level: 3.67 m)

Level 2: 2.56 m (Level: 7.34 m)

Level 3: 2.87 m (Level: 11.01 m)

Level 4: 2.62 m (Level: 15.11 m)







