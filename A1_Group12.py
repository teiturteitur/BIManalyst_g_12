########################################################
'''
The following script takes an element type as input (e.g. IfcDuctSegment) 
and checks if it is defined on the correct level in the IFC file. 
If not, it moves the element to the correct level. 
It also checks the distance between the element



'''
########################################################






import ifcopenshell
import ifcopenshell.geom

#load the IFC file
# ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-06-D-MEP.ifc")
# ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-08-D-MEP.ifc")
ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-16-D-MEP.ifc")



# find etage for elementer og sæt dem ind under etagen hvis de er defineret forkert

# hvis det kører over flere etager skal elementerne sættes ind under bygningen i stedet for en specifik etage



# i want to check the distance between the ducts and the floor (level) in the ifc file
hvacElements = ifc_file.by_type("IfcDuctSegment") + ifc_file.by_type("IfcAirTerminal")



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
    

def getElementZCoordinate(element):
    shape = ifcopenshell.geom.create_shape(settings, element)
    vertices = shape.geometry.verts
    z_values = vertices[2::3]  # Extract every third value starting from index 2 (z-coordinates)
    if z_values:
        return min(z_values)  # Return the minimum z-coordinate
    else:
        print("No vertices found for element")
        return None


FreeHeights = {}

for element in hvacElements:
    element_z = getElementZCoordinate(element)
    level, name = getLevelElevation(element)
    if element_z is not None and level is not None:
        free_height = element_z - level
        if FreeHeights.get(name) is None:
            FreeHeights[name] = free_height, level, element
        # elif free_height < FreeHeights.get(name)[0]:
        elif free_height < FreeHeights.get(name)[0] and free_height > 1: # to avoid elements defined to the wrong level
            FreeHeights[name] = free_height, level, element
        else:
            continue


# Sort FreeHeights by level and print results
FreeHeights = dict(sorted(FreeHeights.items(), key=lambda item: item[1][1]))
for name, (free_height, level, element) in FreeHeights.items():
    print(f"\nFree height for {name}: {round(free_height,2)} m (Level: {round(level,2)} m)")



def ChangeColor(elements, lowestPoint):

    # Create a red RGB color (values between 0–1)
    red_color = ifc_file.create_entity("IfcColourRgb", Name="Red", Red=1.0, Green=0.0, Blue=0.0)
    yellow_color = ifc_file.create_entity("IfcColourRgb", Name="Yellow", Red=1.0, Green=1.0, Blue=0.0)

    counter = 0

    for element in elements:
        if lowestPoint[counter] < 2.6:
            color = red_color
        else:
            color = yellow_color
        # Create a surface shading style
        surface_style = ifc_file.create_entity(
            "IfcSurfaceStyle",
            Name="RedSurface",
            Side="BOTH",
            Styles=[ifc_file.create_entity("IfcSurfaceStyleShading", SurfaceColour=color)]
        )

        if not element.Representation:
            print(f"No representation for element {element.GlobalId}")
            continue
        
        representations = element.Representation.Representations
        if not representations or not representations[0].Items:
            print(f"No items for element {element.GlobalId}")
            continue
        
        representation_item = representations[0].Items[0]

        # Attach the style directly via IfcStyledItem
        ifc_file.create_entity(
            "IfcStyledItem",
            Item=representation_item,
            Styles=[surface_style],
            Name=None
        )
        counter += 1

# Change color of the lowest duct to red in the ifc file
lowest_duct = [FreeHeights[level][2] for level in FreeHeights]
lowestPoint = [FreeHeights[level][0] for level in FreeHeights]


ChangeColor(lowest_duct, lowestPoint)
# print([lowest_duct])

# save the ifc file to desktop
newFileName = "TEST3.ifc"
ifc_file.write("/Users/teiturheinesen/Desktop/" + newFileName)
print("IFC file saved to desktop as " + newFileName)

