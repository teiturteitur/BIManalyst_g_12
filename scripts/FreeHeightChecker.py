import ifcopenshell
import ifcopenshell.geom
from .functions import getElementZCoordinate, getLevelElevation



def FreeHeightChecker(ifc_file, elementType='IfcDuctSegment', minFreeHeight=2.6, colorQuestion=True):

    FreeHeights = {}

    targetElements = ifc_file.by_type(elementType)
    
    for element in targetElements:
        element_z = getElementZCoordinate(element=element)
        level, name = getLevelElevation(ifc_file=ifc_file,element=element)
        if level is False:
            # element is assigned to building, not a storey
            print(f"⚠️ Element {element.GlobalId} is assigned to the building - Skipping")
            targetElements.remove(element)
            continue
        else:
            if element_z is not None and level is not None:
                # print(f"{element.GlobalId}: {element_z} m - Level: {round(level,2)} m")
                free_height = element_z[0] - level
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

    # Change color of the lowest duct to red in the ifc file
    lowest_duct = [FreeHeights[level][2] for level in FreeHeights]
    lowestPoint = [FreeHeights[level][0] for level in FreeHeights]


    if colorQuestion is True:
        # Create a red RGB color (values between 0–1)
        red_color = ifc_file.create_entity("IfcColourRgb", Name="Red", Red=1.0, Green=0.0, Blue=0.0)
        yellow_color = ifc_file.create_entity("IfcColourRgb", Name="Yellow", Red=1.0, Green=1.0, Blue=0.0)

        counter = 0

        for element in lowest_duct:
            # print(f'{lowestPoint=}, {counter=}')
            if counter >= len(lowestPoint):
                continue
            elif lowestPoint[counter] < minFreeHeight:
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

    return ifc_file


