import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.api.spatial
from .functions import getElementZCoordinate, getLevelElevation, ChangeColor

 
def ElementLevelChecker(ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-16-D-MEP.ifc"), 
                        elementType="IfcDuctSegment", colorQuestion=True):



    # i want to check the distance between the ducts and the floor (level) in the ifc file
    targetElements = ifc_file.by_type(elementType)




    levelElevations = {storey: round(storey.Elevation / 1000,2) for storey in ifc_file.by_type('IfcBuildingStorey')}
    print(list(levelElevations.values()))

    # check hvacElements for their z coordinate and designated level - if element is not on the right level, move it to the right level

    levelKeys = list(levelElevations.keys())



    elementCounter = 0
    for element in targetElements:
        minZ, maxZ = getElementZCoordinate(element=element)
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

                            # print(f"\n🟨 Element {elementCounter} - Designated level: {round(level,2)} \n FOUND CORRECT LEVEL! ({val}) Element height: {round(maxZ-minZ,3)}. \n {minZ=} \n {maxZ=} 🟨")
                            if colorQuestion is True:
                                ChangeColor(ifc_file=ifc_file, element=element, colorChoice='Y')

                            ifcopenshell.api.spatial.assign_container(ifc_file, products=[element], relating_structure=key)
                            print(f"🟨 Element {elementCounter} moved to level {key.Name}. 🟨 \n")
            
                            elementCounter += 1
                            break

                    else:
                        if levelCounter+1 <= len(levelKeys)-1: # avoid index error
                            levelCounter += 1
                            continue
                        else:
                            # print(f"\n🔝 Element {elementCounter} - Designated level: {round(level,2)} \n Above highest level! Element height: {round(maxZ-minZ,3)}. \n {minZ=} \n {maxZ=} 🔝")
                            elementCounter += 1
                            break
                    
                elif minZ < val and maxZ > val: # between two levels!
                    # print(f"\n⛔ Element {elementCounter} - Designated level: {round(level,2)} \n Between two levels! ({val}) Element height: {round(maxZ-minZ,3)}. \n {minZ=} \n {maxZ=} ⛔")
                    if colorQuestion is True:
                        ChangeColor(ifc_file=ifc_file, element=element, colorChoice='R')
                    # get current building of element
                    buildings = ifc_file.by_type("IfcBuilding")
                    if buildings:
                        building = buildings[0]  # Assuming there's only one building in the IFC file!!!!!!!!
                        ifcopenshell.api.spatial.assign_container(ifc_file, products=[element], relating_structure=building)
                    print(f"⛔ Element {elementCounter} moved to building {building.Name} - between levels. ⛔ \n  ")

                    elementCounter += 1
                    break
                
                

        
        else:
            print(f"Could not determine free height for element {element.GlobalId}")


    return ifc_file



