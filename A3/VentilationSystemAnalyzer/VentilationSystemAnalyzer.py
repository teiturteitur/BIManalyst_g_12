"""
This file aims to cross-reference MEP IFC files with a corresponding architectural IFC file to check if the ventilation systems are dimensioned and modeled correctly.

Version: 23/11/25

The following checks are perfomed:
    - Do all ventilation systems (IfcDistributionSystem) have an air handling unit assigned?
    - What space is each IfcAirTerminal placed in? And are all air terminals placed in a space?
    - Which spaces do NOT have an air terminal assigned?
    - When air flow and pressure loss is defined for all ventilation elements, are these values respectable?


Input:
    Console
        Rich.Console()
            Used for tables and visualization.
    MEP_file
        MEP file with ventilation systems.
    Space_file
        IFC file containing spaces (and Pset_SpaceAirHandlingDimensioning for each space).

Returns:
    BCFXml file
        BCF file with all failed checks.
"""

import ifcopenshell
from ifcopenshell.ifcopenshell_wrapper import Representation
import ifcopenshell.util.system

import ifcopenshell.util.pset
import ifcopenshell.util.element

# import ifcopenshell.util.placement
import ifcopenshell.api.pset
# import ifcopenshell.api.project
import ifcopenshell.geom

# import os
from rich.console import Console

# from rich.prompt import Prompt
from rich.table import Table

# from rich.prompt import Prompt
from rich import inspect
import numpy as np
from treelib.tree import Tree

# import json
# from pressureLossDB import pressure_loss_db
# from functions import get_element_bbox, bbox_overlap


def ahuFinder(
    console: Console,
    ifc_file: ifcopenshell.file,
    targetSystems: str = "IfcDistributionSystem",
) -> tuple[dict, dict, Table]:
    # build dictionaries of systems with and without AHUs.

    identifiedSystems = {}

    ifc_file_systems = ifc_file.by_type(targetSystems)
    # to ensure that only supply and return is in the dictionary, only keep system.Name == 'VU' or 'VI'
    # if system.Name does not contain VU or VI, remove it from the list
    ifc_file_systems = [
        system
        for system in ifc_file_systems
        if "VU" in system.Name or "VI" in system.Name
    ]

    missingAHUsystems = {}
    for system in ifc_file_systems:
        elements = system.IsGroupedBy[0].RelatedObjects

        # remove IfcDistributionPort from list of elements - as these are not relevant for AHU check
        elements = [el for el in elements if not el.is_a("IfcDistributionPort")]
        # console.print(elements)
        # print(f'{[el.is_a() for el in elements]=}')

        uniqueElements = set(elements.is_a() for elements in elements)
        uniqueElementsType = set(elements.ObjectType for elements in elements)

        # the AHU element _should_ be an IfcUnitaryEquipment, but in the given ifc files, they are IfcBuildingElementProxy containing 'Geniox' in their names.
        # in the future, this should just create an instance in the BCF file saying that the system is missing an AHU element.
        if any(e and "IfcUnitaryEquipment" in e for e in uniqueElements):
            identifiedSystems[system.Name] = {
                "ElementCount": len(elements),
                "ElementTypes": list(uniqueElements),
                "ElementIDs": [element.GlobalId for element in elements],
            }
        else:
            # if uniqueElements contains IfcBuildingElementProxy with 'Geniox' in their ObjectType, consider it as having an AHU - remove this in future
            if any("Geniox" in str(e) for e in uniqueElementsType):
                identifiedSystems[system.Name] = {
                    "ElementCount": len(elements),
                    "ElementTypes": list(uniqueElements),
                    "ElementIDs": [element.GlobalId for element in elements],
                }
            else:
                missingAHUsystems[system.Name] = {
                    "ElementCount": len(elements),
                    "ElementTypes": list(uniqueElements),
                    "ElementIDs": [element.GlobalId for element in elements],
                }

    # for all identified systems, find the Supply/Return pairs (the systems using the same AHU) and add a new key 'PairedSystem' to the dictionary
    for systemName, info in identifiedSystems.items():
        elements = info.get("ElementIDs", [])
        ahu_elements = [
            el
            for el in elements
            if ifc_file.by_id(el).is_a("IfcUnitaryEquipment")
            or ("Geniox" in str(ifc_file.by_id(el).ObjectType))
        ]
        pairedSystems = []
        for otherSystemName, otherInfo in identifiedSystems.items():
            if otherSystemName == systemName:
                continue
            other_elements = otherInfo.get("ElementIDs", [])
            other_ahu_elements = [
                el
                for el in other_elements
                if ifc_file.by_id(el).is_a("IfcUnitaryEquipment")
                or ("Geniox" in str(ifc_file.by_id(el).ObjectType))
            ]
            # if any of the ahu_elements are in other_ahu_elements, consider them paired
            if any(ahu in other_ahu_elements for ahu in ahu_elements):
                pairedSystems.append(otherSystemName)
        if pairedSystems:
            identifiedSystems[systemName]["PairedSystems"] = pairedSystems

    # table of AHUs and their respective supply and return systems (with element counts)
    table_AHUs = Table(title="AHU Elements and their Systems", show_lines=True)
    table_AHUs.add_column("AHU Element GlobalId", style="cyan", no_wrap=True)
    table_AHUs.add_column("Supply System (Element Count)", style="red")
    table_AHUs.add_column("Return System (Element Count)", style="blue")

    processed_AHUs = set()

    # VI=Supply, VU=Return
    for systemName, info in identifiedSystems.items():
        elements = info.get("ElementIDs", [])
        ahu_elements = [
            el
            for el in elements
            if ifc_file.by_id(el).is_a("IfcUnitaryEquipment")
            or ("Geniox" in str(ifc_file.by_id(el).ObjectType))
        ]
        for ahu in ahu_elements:
            if ahu in processed_AHUs:
                continue
            supplySystem = systemName if "VI" in systemName else None
            returnSystem = systemName if "VU" in systemName else None
            # check paired systems for the other type
            pairedSystems = info.get("PairedSystems", [])
            for pairedSystem in pairedSystems:
                if "VI" in pairedSystem:
                    supplySystem = pairedSystem
                elif "VU" in pairedSystem:
                    returnSystem = pairedSystem
            supplyCount = (
                identifiedSystems[supplySystem]["ElementCount"] if supplySystem else 0
            )
            returnCount = (
                identifiedSystems[returnSystem]["ElementCount"] if returnSystem else 0
            )
            table_AHUs.add_row(
                ahu,
                f"{supplySystem} ({supplyCount})" if supplySystem else "N/A",
                f"{returnSystem} ({returnCount})" if returnSystem else "N/A",
            )
            processed_AHUs.add(ahu)

    # console.print(table_AHUs)

    console.print(
        f"\n Number of systems WITHOUT AHU elements: [bold red]{len(missingAHUsystems)}[/bold red]\n Number of elements not analyzed: [bold red]{sum(v.get('ElementCount', 0) for v in missingAHUsystems.values())}[/bold red]\n"
    )

    return identifiedSystems, missingAHUsystems, table_AHUs


#######################################
#        The following two functions
#        are for clash detection.
#######################################


def get_element_bbox(element: ifcopenshell.entity_instance) -> dict:
    """Return min/max XYZ coordinates of an IFC element in world coordinates.
    I WANT TO CHANGE THIS TO USE ifcopenshell.util.shape.get_bbox(element) insead!
    """
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    shape = ifcopenshell.geom.create_shape(settings, element)
    verts = np.array(shape.geometry.verts).reshape(-1, 3)

    bbox_min = verts.min(axis=0)
    bbox_max = verts.max(axis=0)

    return {"min": bbox_min, "max": bbox_max}


def bbox_overlap(b1: dict, b2: dict) -> bool:
    return all(
        b1["min"][i] <= b2["max"][i] and b1["max"][i] >= b2["min"][i] for i in range(3)
    )


def airTerminalSpaceClashAnalyzer(
    console: Console,
    MEP_file: ifcopenshell.file,
    space_file: ifcopenshell.file,
    space_file_name: str,
    identifiedSystems: dict,
) -> tuple[dict, dict, Table]:
    """Checks which air terminals are inside which spaces.

    input:
        console: rich.console.Console
            For console printing purposes.
        MEP_file: ifcopenshell.file
            .ifc file with ventilation systems.
        space_file: ifcopenshell.file
            Architectural ifc file with defined spaces WITH Pset_SpaceAirHandlingDimensioning
        identifiedSystems: dict
            output from ahuFinder()

    Returns: A dictionary with space.GlobalId as key and a list of air terminal GlobalIds as values.
    """
    spaces = space_file.by_type("IfcSpace")
    # spaces with a long name of Area should be ignored (in this case, at they mess it up)
    spaces = [space for space in spaces if "Area" not in space.LongName]
    spaces = [space for space in spaces if "Rooftop Terrace" not in space.LongName]

    # space bounding boxes
    space_bboxes = {}
    for space in spaces:
        try:
            bbox = get_element_bbox(space)
            # add 0.5 to max Z to ensure overlap with more air terminals
            bbox["max"][2] += 0.5
            # print(f'Space {space.GlobalId} bbox: {bbox}')
            space_bboxes[space.GlobalId] = {"space": space, **bbox}
        except Exception as e:
            console.print(f"[yellow]Skipping space {space.GlobalId}: {e}[/yellow]")

    spaceTerminals = {}
    unassignedTerminals = {"Supply": [], "Return": []}

    for systemName, info in identifiedSystems.items():
        # analyzing each system

        # identify air terminals
        elements = info.get("ElementIDs", [])
        # print(f"System {systemName}: {elements}")
        air_terminals = [
            el for el in elements if MEP_file.by_id(el).is_a("IfcAirTerminal")
        ]
        # console.print(f"System {systemName}: {air_terminals}")

        for air_terminal in air_terminals:
            # print(f'Analyzing air terminal {air_terminal.GlobalId}, {air_terminal=}')
            try:
                # get bounding box of air terminal
                at_bbox = get_element_bbox(MEP_file.by_id(air_terminal))
            except Exception as e:
                console.print(
                    f"[yellow]Skipping air terminal {air_terminal}: {e}[/yellow]"
                )
                continue

            # check which space the air terminal bounding box overlaps with
            found_space = None
            for sid, sdata in space_bboxes.items():
                if bbox_overlap(at_bbox, sdata):
                    found_space = sdata["space"]
                    # air terminal is inside this space
                    break
                else:
                    # air terminal not inside this space
                    continue

            if not found_space:  # unassigned air terminals
                if "VU" in systemName:
                    unassignedTerminals["Return"].append(air_terminal)
                    continue
                elif "VI" in systemName:
                    unassignedTerminals["Supply"].append(air_terminal)
                    continue

            if found_space:
                # console.print(found_space.GlobalId)
                if found_space.GlobalId not in spaceTerminals.keys():
                    spaceTerminals[found_space.GlobalId] = {"Supply": [], "Return": []}
                    # console.print(f"Created new entry for space: {found_space.GlobalId}")

                if "VU" in systemName:
                    spaceTerminals[found_space.GlobalId]["Return"].append(air_terminal)
                elif "VI" in systemName:
                    spaceTerminals[found_space.GlobalId]["Supply"].append(air_terminal)

    # create table with space names and number of air terminals in each space - lastly a row with unnassigned air terminals
    table_spaces = Table(title="Air Terminals in Spaces", show_lines=True)
    table_spaces.add_column(
        f"Space Long Name \n ({space_file_name})", style="green", no_wrap=True
    )
    table_spaces.add_column("Supply Air Terminals", style="red")
    table_spaces.add_column("Return Air Terminals", style="blue")

    for spaceID, terminals in spaceTerminals.items():
        table_spaces.add_row(
            spaceID,
            str(len(terminals.get("Supply", []))),
            str(len(terminals.get("Return", []))),
        )

    # add unassigned row
    table_spaces.add_row(
        "[bold red]Unassigned[/bold red]",
        str(len(unassignedTerminals.get("Supply", []))),
        str(len(unassignedTerminals.get("Return", []))),
    )
    # console.print(table_spaces)

    return spaceTerminals, unassignedTerminals, table_spaces


#######################################
#        The following functions (and class)
#        are for keeping track of the
#        ventilation system routes,
#        element properties, etc.
#        (+ being able to vizualise them!)
#######################################


class elementNode:
    def __init__(
        self,
        IfcType: str,
        airFlow: float,
        element: ifcopenshell.entity_instance,
        elementID: str,
        prevElementID: str,
        elementPorts: list,
    ):
        self.element: ifcopenshell.entity_instance = element
        self.elementID: str = elementID
        self.IfcType: str = IfcType
        self.airFlow: float = airFlow  # in l/s
        self.prevElementID: str = prevElementID
        self.elementPorts = elementPorts
        self.elementPressureLoss = 0  # in Pa - to be calculated
        self.pathPressureLoss = 0  # in Pa - to be calculated

        if element != None:
            self.elementAreaSolid = self.element.Representation.Representations[
                0
            ].Items[0]

            if self.elementAreaSolid.is_a() == "IfcMappedItem":
                pass

            else:
                self.elementSweptArea = (
                    self.element.Representation.Representations[0].Items[0].SweptArea
                )

                self.elementCrossArea, self.elementLength, self.elementDims = (
                    self.getElementDims()
                )

        if not elementPorts:
            self.portOrientations = []
        elif len(elementPorts) == 2:
            # inspect(elementPorts)
            port1_matrix = (
                ifcopenshell.geom.map_shape(
                    settings=ifcopenshell.geom.settings(), inst=elementPorts[0]
                )
                .__getattribute__("matrix")
                .components
            )
            port1 = [port1_matrix[0][3], port1_matrix[1][3], port1_matrix[2][3]]
            port2_matrix = (
                ifcopenshell.geom.map_shape(
                    settings=ifcopenshell.geom.settings(), inst=elementPorts[1]
                )
                .__getattribute__("matrix")
                .components
            )
            port2 = [port2_matrix[0][3], port2_matrix[1][3], port2_matrix[2][3]]
            # find orientation vector
            self.portOrientations = self.getOrientationVector(port1=port1, port2=port2)
            if self.IfcType == "IfcDuctFitting":
                # check if fitting is straight (self.portOrientations consists only of 1s and 0s) or not
                if all(x in (0, 1) for x in self.portOrientations):
                    self.fittingType = "Straight"
                else:
                    self.fittingType = "Bend"

        elif len(elementPorts) > 2:
            self.portOrientations = []

        else:
            self.portOrientations = []

    def __str__(self):
        return f"{self.IfcType} ({self.airFlow})"

    def getOrientationVector(self, port1=None, port2=None) -> np.ndarray:
        # create orientation vector from elementPorts
        vector = np.array(port2) - np.array(port1)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return np.array([0, 0, 0])
        return np.round(vector / norm, 2)

    def getElementDims(self) -> tuple:
        """
        Only works for IfcDuctElements with IfcCircleProfileDef or IfcRectangleProfileDef
        """
        if self.element.is_a() not in ["IfcDuctSegment"]:
            # print(f'Element {self.element.is_a()} has unsupported profile definition: {self.elementAreaSolid.is_a()}')
            # inspect(self.elementAreaSolid)
            return 0, 0, {}

        if self.elementSweptArea.is_a() == "IfcCircleProfileDef":
            crossArea = np.pi * (self.elementSweptArea.Radius / 1000) ** 2  # m2
            elementLength = round(self.elementAreaSolid.Depth / 1000, 3)  # m
            elementDims = {
                "Diameter_m": round(self.elementSweptArea.Radius * 2 / 1000, 3)
            }

        elif self.elementSweptArea.is_a() == "IfcRectangleProfileDef":
            crossArea = (
                min(
                    self.elementSweptArea.XDim,
                    self.elementSweptArea.YDim,
                )
                / 1000
                * self.elementAreaSolid.Depth
                / 1000
            )  # m2
            elementLength = (
                max(
                    self.elementSweptArea.XDim,
                    self.elementSweptArea.YDim,
                )
                / 1000
            )  # m
            elementDims = {
                "Width_m": round(
                    min(
                        self.elementSweptArea.XDim,
                        self.elementSweptArea.YDim,
                    )
                    / 1000,
                    3,
                ),
                "Height_m": round(self.elementAreaSolid.Depth / 1000, 3),
            }

        else:
            # print(f'Element has unsupported profile definition: {self.elementAreaSolid.is_a()}')
            # inspect(self.elementAreaSolid)
            return 0, 0, {}

        return round(crossArea, 3), round(elementLength, 3), elementDims

    def pressureLossDuct(self):
        """
        Calculate pressure loss for duct elements.
        """
        if self.IfcType == "IfcDuctSegment":
            if self.elementCrossArea == 0 or self.elementLength == 0:
                # invalid dimensions
                return None

            # get hydraulic diameter (D_h)
            if self.elementDims.get("Diameter_m"):
                # circular duct
                D_h = (
                    4
                    * ((np.pi * self.elementDims.get("Diameter_m") ** 2) / 4)
                    / (np.pi * self.elementDims.get("Diameter_m"))
                )  # m

            elif self.elementDims.get("Width_m") and self.elementDims.get("Height_m"):
                # rectangular duct
                D_h = (
                    2
                    * self.elementDims.get("Height_m")
                    * self.elementDims.get("Width_m")
                ) / (
                    self.elementDims.get("Height_m") + self.elementDims.get("Width_m")
                )  # m
            else:
                return None

            # Convert air flow from l/s to m3/s
            Q = self.airFlow / 1000  # m3/s

            # Calculate velocity (v = Q / A)
            v = Q / self.elementCrossArea  # m/s

            # Air properties at 20°C
            rho = 1.2041  # kg/m3
            mu = 1.81e-5  # Pa.s

            # Calculate Reynolds number (Re = (rho * v * D_h) / mu)
            Re = (rho * v * D_h) / mu

            # Determine friction factor (f) using the Blasius correlation for turbulent flow
            if Re < 2000:
                f_lambda = 64 / (Re + 1e-10)  # Laminar flow
            else:
                f_lambda = 0.3164 * Re**-0.25  # Turbulent flow

            # dynamic pressure
            # p_d = 1/2 * rho * v**2 # Pa/m
            p_d = 0.5 * rho * v**2  # Pa/m

            # Calculate pressure loss (ΔP = f * (p_d/D_h))
            delta_P = f_lambda * (p_d / D_h)

            self.elementPressureLoss = round(
                delta_P * self.elementLength, 2
            )  # Store pressure loss in Pascals

        elif self.IfcType == "IfcDuctFitting":
            if "BU" in str(self.element.ObjectType):
                # Bend
                self.elementPressureLoss = 10  # Pa (assumed value)

            # if len(self.elementPorts) == 2:
            # PRESSURE LOSS ESTIMATION OF DUCT FITTINGS HAVE NOT BEEN IMPLEMENTED YET!
            # The pressure loss of all duct fittings are therefore assumed to be 0.2 Pa
            else:
                # not bend
                self.elementPressureLoss = 10  # Pa (assumed value)

        elif self.IfcType == "IfcAirTerminal":
            # PRESSURE LOSS ESTIMATION OF AIR TERMINALS IS NOT IMPLEMENTED YET!
            self.elementPressureLoss = 0.2  # Pa (assumed value)


def build_downstream_tree(
    element: ifcopenshell.entity_instance,
    ifc_file: ifcopenshell.file,
    system_name: str,
    tree: Tree,
    parent_id: str,
    visited: set,
) -> Tree:
    """
    Recursively build a tree structure of connected elements downstream from a given AHU using treelib.
    Each node contains: GlobalId as identifier, and data with IfcType and airFlow.
    """

    # # STOP if already visited
    # if element.GlobalId in visited:
    #     return None

    visited.add(element.GlobalId)

    # # STOP if already created in the tree
    # if identifier in tree.nodes:
    #     return None

    # inspect(ifcopenshell.geom.ShapeType(element))
    elementNodeData = elementNode(
        element=element,
        elementID=element.GlobalId,
        IfcType=element.is_a(),
        airFlow=0,
        prevElementID=parent_id,
        elementPorts=ifcopenshell.util.system.get_ports(element),
    )  # Placeholder for air flow value

    # if parent_id is system_name, set tag to 'AHU' and only add child with same system_name
    if parent_id == system_name:
        tag = "AHU"
        identifier = f"{system_name}_{element.GlobalId}"
        new_parent_id = identifier
    else:
        tag = element.GlobalId
        identifier = element.GlobalId
        new_parent_id = identifier

    tree.create_node(
        tag=tag, identifier=identifier, parent=parent_id, data=elementNodeData
    )

    # Get all downstream connections
    # CHANGE THIS TO: Flow direction!!! is more reliable!!
    if "VI" in system_name:
        downstream = ifcopenshell.util.system.get_connected_from(element)
    elif "VU" in system_name:
        downstream = ifcopenshell.util.system.get_connected_to(element)
    else:
        raise ValueError(f"Unable to determine flow direction for {system_name}")

    # Keep only elements in the same system
    downstream = [
        el
        for el in downstream
        if system_name
        in [sys.Name for sys in ifcopenshell.util.system.get_element_systems(el)]
    ]

    for child in downstream:
        if child.GlobalId not in visited:
            build_downstream_tree(
                child, ifc_file, system_name, tree, new_parent_id, visited
            )

    return tree


def getSystemTrees(
    console: Console,
    identifiedSystems: dict,
    ifc_file: ifcopenshell.file,
    space_file: ifcopenshell.file,
    spaceTerminals: dict,
    showChoice=str,
) -> tuple[Tree, ifcopenshell.file]:
    """
    Create tree structures for each identified system showing how elements are connected.
    """
    systemsTree = Tree()
    systemsTree.create_node(
        "Systems",
        "SystemsRoot",
        data=elementNode(
            IfcType="Root",
            airFlow=0,
            element=None,
            elementID="",
            prevElementID="",
            elementPorts=None,
        ),
    )  # give the root a data object with a .type attribute so show(data_property="type") works

    for systemName, info in identifiedSystems.items():
        visited = set()

        # find AHU in system
        systemAHU_ID = [
            el
            for el in info.get("ElementIDs", [])
            if ifc_file.by_id(el).is_a("IfcUnitaryEquipment")
            or ("Geniox" in str(ifc_file.by_id(el).ObjectType))
        ]
        # start at AHU and work downstream
        systemAHU = ifc_file.by_id(systemAHU_ID[0])

        # tree = build_downstream_tree(systemAHU, ifc_file, systemName, visited)
        subTree = systemsTree.create_node(
            systemName,
            systemName,
            parent="SystemsRoot",
            data=elementNode(
                IfcType=systemAHU.is_a(),
                airFlow=0,
                element=None,
                elementID=None,
                prevElementID=None,
                elementPorts=None,
            ),
        )  # root node for the system

        build_downstream_tree(
            systemAHU, ifc_file, systemName, systemsTree, systemName, visited
        )

    # get all paths to air terminals (leaves)
    all_paths = systemsTree.paths_to_leaves()
    # console.print([len(path) for path in all_paths])
    # all_paths = [path[2:] for path in all_paths_dirty if len(path) > 2]

    # inspect(identifiedSystems.keys())
    for path in all_paths:
        pathTerminal = path[-1]
        requiredAirFlow = 0

        if pathTerminal in list(identifiedSystems.keys()):
            inspect(pathTerminal)
            pass

        if (
            "VI"
            in ifcopenshell.util.system.get_element_systems(
                ifc_file.by_id(pathTerminal)
            )[0].Name
        ):
            # Supply systems
            # find air terminal in spaceAirFlows to get required air flow
            for spaceID in spaceTerminals.keys():
                if pathTerminal in [
                    at for at in spaceTerminals[spaceID].get("Supply", [])
                ]:
                    # inspect(spaceTerminals[spaceID])
                    requiredAirFlow = ifcopenshell.util.element.get_pset(
                        element=space_file.by_guid(spaceID),
                        name="Pset_SpaceAirHandlingDimensioning",
                        prop="DesignAirFlow",
                    ) / len(spaceTerminals[spaceID].get("Supply", []))

                    terminalPset = ifcopenshell.api.pset.add_pset(file=ifc_file, product=ifc_file.by_guid(pathTerminal), name='Pset_AirTerminalOccurence')
                    ifcopenshell.api.pset.edit_pset(file=ifc_file, pset=terminalPset, properties={'AirFlowRate': requiredAirFlow})

                    break
        elif (
            "VU"
            in ifcopenshell.util.system.get_element_systems(
                ifc_file.by_id(pathTerminal)
            )[0].Name
        ):
            # Return systems
            for spaceID in spaceTerminals.keys():
                if pathTerminal in [
                    at for at in spaceTerminals[spaceID].get("Return", [])
                ]:
                    requiredAirFlow = ifcopenshell.util.element.get_pset(
                        element=space_file.by_guid(spaceID),
                        name="Pset_SpaceAirHandlingDimensioning",
                        prop="DesignAirFlow",
                    ) / len(spaceTerminals[spaceID].get("Return", []))

                    terminalPset = ifcopenshell.api.pset.add_pset(file=ifc_file, product=ifc_file.by_guid(pathTerminal), name='Pset_AirTerminalOccurence')
                    ifcopenshell.api.pset.edit_pset(file=ifc_file, pset=terminalPset, properties={'AirFlowRate': requiredAirFlow})

                    break

        # assign requiredAirFlow to all elements in path EXCEPT the root (systemName)
        for node_id in path[2:]:
            systemsTree[node_id].data.airFlow += requiredAirFlow
            systemsTree[
                node_id
            ].data.pressureLossDuct()  # update pressure loss based on new air flow

            if systemsTree[node_id].data.prevElementID != None:
                parent_pl = systemsTree[
                    systemsTree[node_id].data.prevElementID
                ].data.pathPressureLoss

                systemsTree[node_id].data.pathPressureLoss = round(
                    systemsTree[node_id].data.elementPressureLoss + parent_pl, 2
                )


    if showChoice == "y":
        systemsTree.show(
            idhidden=False, data_property="pathPressureLoss", line_type="ascii-em"
        )

    return systemsTree, ifc_file


def buildErrorDict(missingAHUsystems: dict, unassignedTerminals: dict, ifc_file: ifcopenshell.file) -> dict:
    """
    Convert HVAC error dictionaries into a  elements_dict format.
    
    Returns a dict for `generate_bcf_from_ifc_elements()`.
    """
    elements_dict = {}

    # DEPRECATED
    # # 1. Misplaced elements (from ElementLevelChecker)
    # for category, elements in misplacedElements.items():
    #     items = []
    #     for guid, e in elements.items():
    #         element = ifc_file.by_id(guid)
    #         msg_lines = [
    #             f"Element Type: {e.get('elementType','Unknown')}",
    #             f"Issue Category: {category}"
    #         ]
    #         if 'originalLevel' in e and 'newLevel' in e:
    #             msg_lines.append(
    #                 f"Moved from {e['originalLevel']} (elev {e.get('originalLevelElevation')}) "
    #                 f"to {e['newLevel']} (elev {e.get('newLevelElevation')})"
    #             )
    #         if 'minZ' in e and 'maxZ' in e:
    #             msg_lines.append(
    #                 f"Min Z: {e['minZ']}, Max Z: {e['maxZ']}, Height: {e.get('elementHeight')}"
    #             )
    #         items.append({
    #             "element": element,
    #             "message": "\n".join(msg_lines)
    #         })
    #     elements_dict[category] = items


    # 2. Missing AHU systems
    for sys_name, info in missingAHUsystems.items():
        system_elements = [ifc_file.by_id(el_id) for el_id in info.get("ElementIDs", [])]
        if not system_elements:
            continue
        msg = (
            f"Distribution system '{sys_name}' contains {info.get('ElementCount',0)} elements "
            f"but no AHU (IfcUnitaryUnit/Geniox element) was found.\n"
            f"Element types: {info.get('ElementTypes','Unknown')}"
        )
        elements_dict[f"Missing AHU - {sys_name}"] = [{"element": system_elements, "message": msg}]

    # 3. Unassigned terminals
    for flow_dir, element_ids in unassignedTerminals.items():
        items = []
        for el_id in element_ids:
            element = ifc_file.by_id(el_id)
            msg = f"Air terminal {el_id} ({flow_dir}) is not located inside an IfcSpace."
            items.append({"element": element, "message": msg})
        elements_dict[f"Unassigned Terminals - {flow_dir}"] = items

    return elements_dict

def modulePipeline(console, MEP_file, space_file):
    # first function
    identifiedSystems, missingAHUsystems, table_AHUs = ahuFinder(
        console, MEP_file, targetSystems="IfcDistributionSystem"
    )

    # second function
    spaceTerminals, unassignedTerminals, table_Spaces = airTerminalSpaceClashAnalyzer(
        console,
        MEP_file,
        space_file,
        identifiedSystems=identifiedSystems,
        space_file_name="25-10-D-ARCH.ifc",
    )

    systemsTree, ifc_file_new = getSystemTrees(
        console=console,
        identifiedSystems=identifiedSystems,
        ifc_file=MEP_file,
        space_file=space_file,
        spaceTerminals=spaceTerminals,
    )


    return identifiedSystems, missingAHUsystems, table_AHUs, spaceTerminals, unassignedTerminals, table_Spaces, systemsTree, ifc_file_new

# console = Console()
# MEP_file = ifcopenshell.open(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/A3/ifcFiles/25-10-D-MEP.ifc"
# )
# space_file = ifcopenshell.open(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/A3/outputFiles/new_25-10-D-ARCH.ifc"
# )
# modulePipeline(console, MEP_file, space_file)
