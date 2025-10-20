import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.api.spatial
import numpy as np


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


def get_element_bbox(element):
    """Return min/max XYZ coordinates of an IFC element in world coordinates."""
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    shape = ifcopenshell.geom.create_shape(settings, element)
    verts = np.array(shape.geometry.verts).reshape(-1, 3)

    bbox_min = verts.min(axis=0)
    bbox_max = verts.max(axis=0)

    return {"min": bbox_min, "max": bbox_max}

# new function should check all air terminals in each system, check if they clash with a space, and if so, add the required air flow to the system.
# then, check if the ducts in the system are dimensioned correctly for the required air flow    
def bbox_overlap(b1, b2):
    return all(
        b1["min"][i] <= b2["max"][i] and b1["max"][i] >= b2["min"][i]
        for i in range(3)
    )

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
   