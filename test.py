
import ifcopenshell.util.element as util
import os
import ifcopenshell
from ifcopenshell.util.element import copy_deep
import ifcopenshell.guid


import ifcopenshell
import ifcopenshell.guid
from ifcopenshell.util.element import copy_deep

def copy_space_with_full_metadata(source_space, target_ifc):
    """Copy an IfcSpace including property and quantity sets."""
    new_space = copy_deep(target_ifc, source_space)

    # Copy all property/quantity sets (Psets + QSets)
    for rel in getattr(source_space, "IsDefinedBy", []):
        propdef = rel.RelatingPropertyDefinition
        new_propdef = target_ifc.add(propdef)

        target_ifc.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[new_space],
            RelatingPropertyDefinition=new_propdef,
            Name=rel.Name,
            Description=rel.Description
        )

    return new_space


def get_space_storey_name(space, model):
    """Find the storey name that contains the given space (works for IFC2x3 and IFC4+)."""
    # Try IFC2x3-style direct attribute
    if hasattr(space, "ContainedInStructure"):
        rels = space.ContainedInStructure
        if rels:
            return rels[0].RelatingStructure.Name

    # IFC4+ style inverse search
    for rel in model.by_type("IfcRelContainedInSpatialStructure"):
        if space in rel.RelatedElements:
            return rel.RelatingStructure.Name

    return None


def attach_space_to_storey_by_name(target_ifc, space, storey_name):
    """Attach a space to a storey in target_ifc with the same name."""
    for storey in target_ifc.by_type("IfcBuildingStorey"):
        if storey.Name == storey_name:
            target_ifc.create_entity(
                "IfcRelContainedInSpatialStructure",
                GlobalId=ifcopenshell.guid.new(),
                RelatedElements=[space],
                RelatingStructure=storey
            )
            return storey
    print(f"[!] Storey '{storey_name}' not found in target IFC.")
    return None


def merge_spaces_with_quantities_and_structure(source_ifc, target_ifc):
    """Copy all spaces (with Psets/QSets) and attach to matching storeys by name."""
    copied_spaces = []

    for source_space in source_ifc.by_type("IfcSpace"):
        new_space = copy_space_with_full_metadata(source_space, target_ifc)
        storey_name = get_space_storey_name(source_space, source_ifc)

        if storey_name:
            attach_space_to_storey_by_name(target_ifc, new_space, storey_name)
        else:
            print(f"[!] Space {source_space.GlobalId} not linked to any storey")

        copied_spaces.append(new_space)

    print(f"Copied {len(copied_spaces)} spaces with quantities and attached to storeys.")
    return copied_spaces


# Example usage
source_ifc = ifcopenshell.open("ifcFiles/25-10-D-ARCH.ifc")
target_ifc = ifcopenshell.open("ifcFiles/25-10-D-MEP.ifc")

merge_spaces_with_quantities_and_structure(source_ifc, target_ifc)
target_ifc.write("ifcFiles/merged_model.ifc")
