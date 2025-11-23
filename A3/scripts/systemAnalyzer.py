"""
This function analyzes the IfcBuildingSystems in an IFC file and checks if any of them are missing an air handling unit (AHU) element.

if an IfcBuildingSystem does NOT contain an AHU element, it will be reported as output.

All IfcBuildingSystems _CONTAINING_ an AHU element will be further analyzed, to check if the system is dimensioned correctly for the required air flow.



Authors: s214310, s203493, s201348
"""

import ifcopenshell
from ifcopenshell.ifcopenshell_wrapper import Representation
import ifcopenshell.util.system

import ifcopenshell.util.pset
import ifcopenshell.util.element

# import ifcopenshell.util.placement
# import ifcopenshell.api
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
from .functions import get_element_bbox, bbox_overlap


def systemAnalyzer(
    console: Console,
    ifc_file: ifcopenshell.file,
    targetSystems: str = "IfcDistributionSystem",
) -> tuple[dict, dict]:
    # build dictionaries of systems with and without AHUs.

    identifiedSystems = {}

    ifc_file_systems = ifc_file.by_type(targetSystems)
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

    console.print(table_AHUs)

    console.print(
        f"\n Number of systems WITHOUT AHU elements: [bold red]{len(missingAHUsystems)}[/bold red]\n Number of elements not analyzed: [bold red]{sum(v.get('ElementCount', 0) for v in missingAHUsystems.values())}[/bold red]\n"
    )

    return identifiedSystems, missingAHUsystems


def pressureLossAnalyzer(
    console: Console,
    ifc_file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    requiredAirFlow: float,
    elementDescription: str,
):
    """
    This function aims to find an estimation of the pressure loss of air flowing through an element in an IFC file.

    Available elements: Ducts and Fittings

    Input:
        console - rich console for printing
        ifc_file - ifcopenshell opened ifc file
        element - ifcopenshell entity instance of the element to analyze
        requiredAirFlow - float, required air flow in l/s

    As of this version, the k value is set to 150 µm and the temperature of the air is 20°C.
    Furthermore all bends are assumed to be 90 degree bends.

    """

    if elementDescription == "Straight Duct":
        pass

    # rho = 1.2041  # kg/m3 - density of air at 20°C
    # v = requiredAirFlow / 1000  # m3/s - convert l/s to m3/s
    # p_d = 1/2 * rho * v**2 # dynamic pressure

    # reductions


################
# Treelib stuff
################


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
        self.pressureLoss = None  # in Pa - to be calculated

        if element != None:
            self.elementAreaSolid = (
                self.element.get_info("Representation")
                .get("Representation")
                .get_info("Representations")
                .get("Representations")[0]
                .get_info("Representations")
                .get("Items")[0]
            )
            self.elementSweptArea = self.elementAreaSolid.get_info("SweptArea").get(
                "SweptArea"
            )
            self.elementCrossArea, self.elementLength, self.elementDims = (
                self.getElementDims()
            )
        else:
            self.elementAreaSolid = None
            self.elementSweptArea = None
            self.elementCrossArea = 0
            self.elementLength = 0
            self.elementDims = {}

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
            crossArea = (
                np.pi
                * (self.elementSweptArea.get_info("Radius").get("Radius") / 1000) ** 2
            )  # m2
            elementLength = round(
                self.elementAreaSolid.get_info("Depth").get("Depth") / 1000, 3
            )  # m
            elementDims = {
                "Diameter_m": round(
                    self.elementSweptArea.get_info("Radius").get("Radius") * 2 / 1000, 3
                )
            }

        elif self.elementSweptArea.is_a() == "IfcRectangleProfileDef":
            crossArea = (
                min(
                    self.elementSweptArea.get_info("XDim").get("XDim"),
                    self.elementSweptArea.get_info("YDim").get("YDim"),
                )
                / 1000
                * self.elementAreaSolid.get_info("Depth").get("Depth")
                / 1000
            )  # m2
            elementLength = (
                max(
                    self.elementSweptArea.get_info("XDim").get("XDim"),
                    self.elementSweptArea.get_info("YDim").get("YDim"),
                )
                / 1000
            )  # m
            elementDims = {
                "Width_m": round(
                    min(
                        self.elementSweptArea.get_info("XDim").get("XDim"),
                        self.elementSweptArea.get_info("YDim").get("YDim"),
                    )
                    / 1000,
                    3,
                ),
                "Height_m": round(
                    self.elementAreaSolid.get_info("Depth").get("Depth") / 1000, 3
                ),
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

            self.pressureLoss = round(
                delta_P * self.elementLength, 2
            )  # Store pressure loss in Pascals

        elif self.IfcType == "IfcDuctFitting":
            if "BU" in str(self.element.get_info("ObjectType").get("ObjectType")):
                # Bend
                self.pressureLoss = 10  # Pa (assumed value)

            # if len(self.elementPorts) == 2:
            # PRESSURE LOSS ESTIMATION OF DUCT FITTINGS HAVE NOT BEEN IMPLEMENTED YET!
            # The pressure loss of all duct fittings are therefore assumed to be 0.2 Pa
            else:
                # not bend
                self.pressureLoss = 10  # Pa (assumed value)

        elif self.IfcType == "IfcAirTerminal":
            # PRESSURE LOSS ESTIMATION OF AIR TERMINALS IS NOT IMPLEMENTED YET!
            self.pressureLoss = 0.2  # Pa (assumed value)


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
    visited.add(element.GlobalId)

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


def findSystemTrees(
    console: Console,
    identifiedSystems: dict,
    ifc_file: ifcopenshell.file,
    spaceAirFlows: dict,
    showChoice=str,
) -> Tree:
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

    for path in all_paths:
        pathTerminal = path[-1]
        requiredAirFlow = 0

        if (
            "VI"
            in ifcopenshell.util.system.get_element_systems(
                ifc_file.by_id(pathTerminal)
            )[0].Name
        ):
            # Supply systems
            # find air terminal in spaceAirFlows to get required air flow
            for spaceID, data in spaceAirFlows.items():
                if pathTerminal in [at for at in data.get("SupplyTerminals", [])]:
                    requiredAirFlow = data.get("SupplyAirFlow", 0)
                    break
        elif (
            "VU"
            in ifcopenshell.util.system.get_element_systems(
                ifc_file.by_id(pathTerminal)
            )[0].Name
        ):
            # Return systems
            for spaceID, data in spaceAirFlows.items():
                if pathTerminal in [at for at in data.get("ReturnTerminals", [])]:
                    requiredAirFlow = data.get("ReturnAirFlow", 0)
                    break
        # assign requiredAirFlow to all elements in path EXCEPT the root (systemName)
        for node_id in path[1:]:
            systemsTree[node_id].data.airFlow += requiredAirFlow
            systemsTree[
                node_id
            ].data.pressureLossDuct()  # update pressure loss based on new air flow

    if showChoice == "y":
        systemsTree.show(idhidden=False, data_property="airFlow", line_type="ascii-em")

    return systemsTree


def airTerminalSpaceClashAnalyzer(
    console: Console,
    MEP_file: ifcopenshell.file,
    space_file_name: str,
    space_file: ifcopenshell.file,
    identifiedSystems: dict,
) -> tuple[dict, dict]:
    """Check which air terminals are inside which spaces.
    Returns: A dictionary with space.GlobalId as key and a list of air terminal GlobalIds as values.
    """
    spaces = space_file.by_type("IfcSpace")
    # spaces with a long name of Area should be ignored
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

    return spaceTerminals, unassignedTerminals


def spaceAirFlowCalculator(
    console: Console,
    MEP_file: ifcopenshell.file,
    space_file: ifcopenshell.file,
    spaceTerminals: dict,
    unassignedTerminals: dict,
) -> dict:
    """Calculate required air flow for each space based on space.LongName and number of air terminals.
    Returns: A dictionary with space.GlobalId as key and required air flow as values.
    """

    # ask for user input for which category the building is (cat I, II, III, IV) - only II implemented

    # building_category = console.input("[bold blue]Enter the building category (I, II, III, IV): [/bold blue]")
    # building_category = building_category.strip().upper()
    # if building_category not in ['I', 'II', 'III', 'IV']:
    #     console.print("[bold red]Invalid building category. Defaulting to II.[/bold red]")
    #     building_category = 'II'
    # else:
    #     console.print(f"[bold green]Building category set to {building_category}.[/bold green]")

    building_category = "II"  # default to II for now

    # According to DS_EN 16798-1:2019
    airFlowDict = {
        "I": {
            "l/s per person": 10,  # l/s per person
            "l/s per area": 1.0,  # l/s per m²
            "l/s backup": 2,  # l/s per m² (if person density is unknown)
        },
        "II": {
            "l/s per person": 7,  # l/s per person
            "l/s per area": 0.7,  # l/s per m²
            "l/s backup": 1.4,  # l/s per m² (if person density is unknown)
        },
        "III": {
            "l/s per person": 4,  # l/s per person
            "l/s per area": 0.4,  # l/s per m²
            "l/s backup": 0.8,  # l/s per m² (if person density is unknown)
        },
        "IV": {
            "l/s per person": 2.5,  # l/s per person
            "l/s per area": 0.3,  # l/s per m²
            "l/s backup": 0.55,  # l/s per m² (if person density is unknown)
        },
    }

    # dont know how to get person density from ifc spaces...
    assumedPersonDensityDict = {
        "Open Office": 17,  # m² per person
        "Closed Office": 10,  # m² per person
        "Classroom": 2,  # m² per person
        "Meeting Room": 2,  # m² per person
        "Auditorium": 5,  # m² per person
        "Backup": 10,  # m² per person
    }

    spaceAirFlows = {}

    # get GrossFloorArea from IfcElementQuantity for all spaces
    spaceAreas = {}

    for spaceID in spaceTerminals.keys():
        if spaceID == "Unassigned":
            continue
        else:
            spaceAreas[spaceID] = 0
            for rel in getattr(space_file.by_guid(spaceID), "IsDefinedBy", []):
                propdef = rel.RelatingPropertyDefinition
                if propdef.is_a("IfcElementQuantity"):
                    for q in propdef.Quantities:
                        if getattr(q, "Name", "") == "GrossFloorArea":
                            spaceAreas[spaceID] = getattr(q, "AreaValue", 0)
                            break
                if spaceAreas[spaceID] != 0:
                    break

    # console.print(f"GrossFloorArea: {spaceAreas}")
    # find amount of chairs in each space in spaceTerminals.keys()
    for spaceID, terminals in spaceTerminals.items():
        if spaceID == "Unassigned":
            continue
        spaceType = space_file.by_guid(spaceID).LongName
        area = spaceAreas.get(space.id(), 0)  # in m²
        spaceElements = space_file.by_guid(spaceID).ContainsElements
        elementsInSpace = [
            spaceElements[element].RelatedElements
            for element in range(len(spaceElements))
        ]
        assumedOccupancy = len(
            [
                el
                for el in elementsInSpace[0]
                if el.is_a("IfcFurniture") and "Chair" in el.Name
            ]
        )
        # console.print(f'{len(chairsInSpace)=} in space {space_file.by_id(spaceID).LongName}')

        if assumedOccupancy > 0:
            requiredAirFlow = (
                airFlowDict[building_category]["l/s per person"] * assumedOccupancy
            ) + (airFlowDict[building_category]["l/s per area"] * area)
            pass

        elif assumedOccupancy == 0:
            console.print(
                f"[yellow]No chairs found in space {space_file.by_id(spaceID).LongName}[/yellow]"
            )
            if spaceType in assumedPersonDensityDict:
                assumedOccupancy = round(
                    spaceAreas.get(spaceID, 0) / assumedPersonDensityDict[spaceType], 2
                )
                requiredAirFlow = (
                    spaceAreas.get(spaceID, 0) / assumedPersonDensityDict[spaceType]
                ) * airFlowDict[building_category]["l/s per person"] + (
                    area * airFlowDict[building_category]["l/s per area"]
                )
            else:
                # use backup values
                assumedOccupancy = round(
                    spaceAreas.get(spaceID, 0) / assumedPersonDensityDict["Backup"], 2
                )
                requiredAirFlow = (
                    spaceAreas.get(spaceID, 0) / assumedPersonDensityDict["Backup"]
                ) * airFlowDict[building_category]["l/s backup"] + (
                    area * airFlowDict[building_category]["l/s per area"]
                )
        else:
            raise ValueError(f"Invalid assumed occupancy: {assumedOccupancy}")

        spaceAirFlows[spaceID] = {
            "SpaceLongName": spaceType,
            "Area_m2": round(area, 2),
            "Assumed_Occupancy": assumedOccupancy,
            "RequiredAirFlow_l_s": round(requiredAirFlow, 2),
            "SupplyTerminals": terminals.get("Supply", []),
            "SupplyAirFlow": round(
                requiredAirFlow / max(1, len(terminals.get("Supply", []))), 2
            )
            if terminals.get("Supply", [])
            else 0,
            "ReturnTerminals": terminals.get("Return", []),
            "ReturnAirFlow": round(
                requiredAirFlow / max(1, len(terminals.get("Return", []))), 2
            )
            if terminals.get("Return", [])
            else 0,
        }

    # table with required air flows per active space
    table_airflows = Table(title="Required Air Flows per Space", show_lines=True)
    table_airflows.add_column("Space Long Name", style="green", no_wrap=True)
    table_airflows.add_column("Area (m²)", style="cyan")
    table_airflows.add_column("Assumed Occupancy", style="cyan")
    table_airflows.add_column("Required Air Flow (l/s)", style="magenta")
    table_airflows.add_column("Supply Terminals", style="red")
    table_airflows.add_column("Supply Air Flow (l/s term.)", style="red")
    table_airflows.add_column("Return Terminals", style="blue")
    table_airflows.add_column("Return Air Flow (l/s term.)", style="blue")
    for spaceID, data in spaceAirFlows.items():
        table_airflows.add_row(
            data["SpaceLongName"],
            str(data["Area_m2"]),
            str(data["Assumed_Occupancy"]),
            str(data["RequiredAirFlow_l_s"]),
            str(len(data["SupplyTerminals"])),
            str(data["SupplyAirFlow"]),
            str(len(data["ReturnTerminals"])),
            str(data["ReturnAirFlow"]),
        )

    if unassignedTerminals:
        table_airflows.add_row(
            "[bold red]Unassigned[/bold red]",
            "-",
            "-",
            "-",
            str(len(unassignedTerminals.get("Supply", []))),
            "-",
            str(len(unassignedTerminals.get("Return", []))),
            "-",
        )

    console.print(table_airflows)

    return spaceAirFlows


# mep_file = ifcopenshell.open(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-10-D-MEP.ifc"
# )
# space_file = ifcopenshell.open(
#     "/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-10-D-ARCH.ifc"
# )
# identifiedSystems, missingAHUsystems = systemAnalyzer(
#     console=Console(), ifc_file=mep_file, targetSystems="IfcDistributionSystem"
# )
# spaceTerminals, unassignedTerminals = airTerminalSpaceClashAnalyzer(
#     console=Console(),
#     MEP_file=mep_file,
#     space_file=space_file,
#     space_file_name="ARCH FILE",
#     identifiedSystems=identifiedSystems,
# )
# spaceAirFlows = spaceAirFlowCalculator(
#     console=Console(),
#     MEP_file=mep_file,
#     space_file=space_file,
#     spaceTerminals=spaceTerminals,
#     unassignedTerminals=unassignedTerminals,
# )
#
# systemsTree = findSystemTrees(
#     console=Console(),
#     identifiedSystems=identifiedSystems,
#     ifc_file=mep_file,
#     spaceAirFlows=spaceAirFlows,
#     showChoice="n",
# )
#
#
# systemsTree.show(idhidden=False, data_property="pressureLoss", line_type="ascii-em")
# # inspect(mep_file.by_type("IfcDuctFitting")[0].get_info("ObjectType").get("ObjectType"))
