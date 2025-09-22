import ifcopenshell
import ifcopenshell.geom
from A1_Group12 import getElementZCoordinate, getLevelElevation

ifc_file = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-16-D-MEP.ifc")
hvacElements = ifc_file.by_type("IfcDuctSegment") + ifc_file.by_type("IfcAirTerminal")


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

