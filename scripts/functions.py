import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.api.spatial


def getLevelElevation(ifc_file, element):
    rels = ifc_file.get_inverse(element)
    for rel in rels:
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                return rel.RelatingStructure.Elevation / 1000, rel.RelatingStructure.Name  # Convert mm to m
            if rel.RelatingStructure.is_a("IfcBuilding"):
                return False, rel.RelatingStructure.Name  # If assigned to building, return elevation 0

    else:
        print("No level found for element")
        return None

def getElementZCoordinate(element):
    # Change ifcopenshell.geom settings to use world coordinates instead of local coordinates
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    shape = ifcopenshell.geom.create_shape(settings, element)
    vertices = shape.geometry.verts
    z_values = vertices[2::3]  # Extract every third value starting from index 2 (z-coordinates)
    if z_values:
        return min(z_values), max(z_values)  # Return the minimum and maximum z-coordinate
    else:
        print("No vertices found for element")
        return None

def ChangeColor(ifc_file, element, colorChoice):

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
   