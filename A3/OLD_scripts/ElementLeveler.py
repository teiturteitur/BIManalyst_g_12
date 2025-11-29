import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.api.spatial
import os
from datetime import datetime
from .functions import getLevelElevation, get_element_bbox
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


def ElementLevelChecker(console: Console, ifc_file: ifcopenshell.file, 
                        targetElements: list[ifcopenshell.entity_instance]) -> tuple[ifcopenshell.file, dict]:

    '''
    Input: ifc_file - ifcopenshell opened ifc file
           targetElements - list of ifc elements to check levels for

    Output: ifc_file - ifcopenshell ifc file with corrected levels
            misplacedElements - dictionary with misplaced elements information
                misplacedElements = {'wrongLevel': {element.GlobalId: {element, other information, ...}},
                                    'betweenLevels': {element.GlobalId: {element, other information, ...}}}
    '''

    # i want to check the distance between the ducts and the floor (level) in the ifc file
    targetElements = targetElements
    misplacedElements = {'wrongLevel': {}, 'betweenLevels': {}}



    levelElevations = {storey: round(storey.Elevation / 1000,2) for storey in ifc_file.by_type('IfcBuildingStorey')}
    # print(list(levelElevations.values()))

    # check hvacElements for their z coordinate and designated level - if element is not on the right level, move it to the right level

    levelKeys = list(levelElevations.keys())



    elementCounter = 0
    for element in targetElements:
        bbox = get_element_bbox(element=element)
        minZ = bbox["min"][2]
        maxZ = bbox["max"][2]
        level, levelName = getLevelElevation(ifc_file= ifc_file, element=element)

        levelCounter = 1
        

        if minZ is not None and level is not None:
            # elementCounter += 1


            for key, val in levelElevations.items():
                # print(f"{key}: {val} m")
                if minZ > val: # above checked level

                    if val < maxZ and maxZ < levelElevations[list(levelElevations.keys())[levelCounter]]:  # Check against the next level

                        if val == round(level,2): # is placed correctly
                            # print(f"\n✅ Element {elementCounter} - Designated level: {round(level,2)} \n Is placed correctly! ({val}) Element height: {round(maxZ-minZ,3)}. \n {minZ=} \n {maxZ=} ✅")
                            elementCounter += 1
                            break

                        else:

                            misplacedElements['wrongLevel'][element.GlobalId] = {
                                'element': element,
                                'elementType': element.is_a(),
                                'originalLevel': levelName,
                                'originalLevelElevation': level,
                                'newLevel': key.Name,
                                'newLevelElevation': round(key.Elevation / 1000,2),
                                'elementHeight': round(maxZ-minZ,3),
                                'minZ': round(minZ,3),
                                'maxZ': round(maxZ,3)
                            }
                            ifcopenshell.api.spatial.assign_container(ifc_file, products=[element], relating_structure=key)
                            # print(f"🟨 Element {elementCounter} moved to level {key.Name}. 🟨 \n")
            
                            elementCounter += 1
                            break

                    else:
                        if levelCounter+1 <= len(levelKeys)-1: # avoid index error
                            levelCounter += 1
                            continue
                        else:
                            # On top level (and correctly placed)
                            elementCounter += 1
                            break
                    
                elif minZ < val and maxZ > val: # between two levels!
                    # print(f"\n⛔ Element {elementCounter} - Designated level: {round(level,2)} \n Between two levels! ({val}) Element height: {round(maxZ-minZ,3)}. \n {minZ=} \n {maxZ=} ⛔")
                    # get current building of element
                    buildings = ifc_file.by_type("IfcBuilding")
                    if buildings:
                        building = buildings[0]  # Assuming there's only one building in the IFC file!!!!!!!!
                        ifcopenshell.api.spatial.assign_container(ifc_file, products=[element], relating_structure=building)
                    # print(f"⛔ Element {elementCounter} moved to building {building.Name} - between levels. ⛔ \n  ")
                    misplacedElements['betweenLevels'][element.GlobalId] =  {
                        'element': element,
                        'elementType': element.is_a(),
                        'originalLevel': levelName,
                        'originalLevelElevation': level,
                        'newRepresentation': building.Name,
                        'elementHeight': round(maxZ-minZ,3),
                        'minZ': round(minZ,3),
                        'maxZ': round(maxZ,3)
                    }

                    elementCounter += 1
                    break
                
                
    # create table of number of misplaced elements
    table = Table(title="Potentially Misplaced Elements")

    table.add_column("Category", justify="center", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")

    table.add_row("Placed on wrong level", str(len(misplacedElements['wrongLevel'])), end_section=True)
    table.add_row("Placed between levels", str(len(misplacedElements['betweenLevels'])),end_section=True)
    table.add_row("Total", str(len(misplacedElements['wrongLevel']) + len(misplacedElements['betweenLevels'])) , end_section=True)

    console.print(table)
    console.print()

    # console.print(f'\n Misplaced Elements Details: {misplacedElements} \n') # remove this later
    return ifc_file, misplacedElements



