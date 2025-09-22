import ifcopenshell
import ifcopenshell.geom

#load the IFC file
# ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-06-D-MEP.ifc")
# ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-08-D-MEP.ifc")
ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-16-D-MEP.ifc")


# i want to check the distance between the ducts and the floor (level) in the ifc file
hvacElements = ifc_file.by_type("IfcDuctSegment")

# hvacElements = ifc_file.by_type("IfcDuctSegment") + ifc_file.by_type("IfcAirTerminal")



# Change ifcopenshell.geom settings to use world coordinates instead of local coordinates
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

def getLevelElevation(element):
    rels = ifc_file.get_inverse(element)
    for rel in rels:
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                return rel.RelatingStructure.Elevation / 1000, rel.RelatingStructure.Name  # Convert mm to m

    else:
        print("No level found for element")
        return None
    
def ElementLevelChanger(element, newLevelName):
    rels = ifc_file.get_inverse(element)
    for rel in rels:
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                    rel.RelatingStructure = newLevelName
                    print(f"Element {element.GlobalId} moved to level {newLevelName}.")
                    break
    return

def getElementZCoordinate(element):
    shape = ifcopenshell.geom.create_shape(settings, element)
    vertices = shape.geometry.verts
    z_values = vertices[2::3]  # Extract every third value starting from index 2 (z-coordinates)
    if z_values:
        return min(z_values), max(z_values)  # Return the minimum and maximum z-coordinate
    else:
        print("No vertices found for element")
        return None

def ChangeColor(element, colorChoice):

    # Create a red RGB color (values between 0–1)
    colors = {'R': ifc_file.create_entity("IfcColourRgb", Name="Red", Red=1.0, Green=0.0, Blue=0.0),
              'Y': ifc_file.create_entity("IfcColourRgb", Name="Yellow", Red=1.0, Green=1.0, Blue=0.0)}
    if colorChoice == 'R':
        surfaceName = "RedSurface"
    elif colorChoice == 'Y':
        surfaceName = "YellowSurface"

    color = colors[colorChoice]
    # Create a surface shading style
    surface_style = ifc_file.create_entity(
        "IfcSurfaceStyle",
        Name=surfaceName,
        Side="BOTH",
        Styles=[ifc_file.create_entity("IfcSurfaceStyleShading", SurfaceColour=color)]
    )

    if not element.Representation:
        print(f"No representation for element {element.GlobalId}")
        return
    
    representations = element.Representation.Representations
    if not representations or not representations[0].Items:
        print(f"No items for element {element.GlobalId}")
        return
    
    representation_item = representations[0].Items[0]

    # Attach the style directly via IfcStyledItem
    ifc_file.create_entity(
        "IfcStyledItem",
        Item=representation_item,
        Styles=[surface_style],
        Name=None
    )
    # print(f"Element {element.GlobalId} colored {color.Name}.")



levelElevations = {storey.Name: round(storey.Elevation / 1000,2) for storey in ifc_file.by_type('IfcBuildingStorey')}
print(list(levelElevations.values()))

# check hvacElements for their z coordinate and designated level - if element is not on the right level, move it to the right level

levelKeys = list(levelElevations.keys())



elementCounter = 0
for element in hvacElements:
    minZ, maxZ = getElementZCoordinate(element)
    level, levelName = getLevelElevation(element)

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
                        
                        ChangeColor(element, colorChoice='Y')
                        
                        # rels = ifc_file.get_inverse(element)
                        # for rel in rels:
                        #     if rel.is_a("IfcRelContainedInSpatialStructure"):
                        #         if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                        #                 print(f'{rel.RelatingStructure=}')
                        #                 rel.RelatingStructure = key              
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

                ChangeColor(element, colorChoice='R')

                elementCounter += 1
                break
              
            

    
    else:
        print(f"Could not determine free height for element {element.GlobalId}")


# save the ifc file to desktop
newFileName = "ElementLevelerTEST.ifc"
ifc_file.write("/Users/teiturheinesen/Desktop/" + newFileName)
print("IFC file saved to desktop as " + newFileName)



