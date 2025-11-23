from datetime import datetime, timezone
import uuid
import ifcopenshell
from bcf.v3.bcfxml import BcfXml
import bcf.v3.visinfo
import bcf.v3.model
from ifcopenshell.util.file import IfcHeaderExtractor
import numpy as np
from rich.console import Console


def iso_now() -> str:
    """Return current UTC time in ISO format with 'Z' suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"


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


def cameraSetup(
    element: ifcopenshell.entity_instance, ifc_file: ifcopenshell.file
) -> tuple[list[float], list[float], list[float]]:
    if isinstance(element, list):
        element = element[0]
    bbox = get_element_bbox(element)
    center = [(bbox["min"][i] + bbox["max"][i]) / 2 for i in range(3)]

    camera_view_point = [
        float(bbox["max"][0] * 1.04),
        float(bbox["max"][1] * 1.04),
        float(bbox["max"][2] * 1.04),
    ]
    camera_direction = [
        float(center[0] - camera_view_point[0]),
        float(center[1] - camera_view_point[1]),
        float(center[2] - camera_view_point[2]),
    ]
    camera_up_vector = [0.0, 0.0, 1.0]

    return camera_view_point, camera_direction, camera_up_vector


def add_bcf_issue(
    bcf_project: BcfXml,
    title: str,
    message: str,
    author: str,
    elements: list | ifcopenshell.entity_instance,
):
    """Add a BCF topic for one or more IFC elements."""
    if not isinstance(elements, list):
        elements = [elements]

    topic = bcf_project.add_topic(title, message, author, "Parameter Validation")
    vp = topic.add_viewpoint(elements[0])
    vp.set_selected_elements(elements)

    cam_pos, cam_dir, cam_up = cameraSetup(elements[0])
    vp.visualization_info.perspective_camera = bcf.v3.visinfo.build_camera_from_vectors(
        camera_position=cam_pos,
        camera_dir=cam_dir,
        camera_up=cam_up,
    )

    topic.comments = [
        bcf.v3.model.Comment(
            guid=str(uuid.uuid4()),
            date=iso_now(),
            author=author,
            comment=message,
            viewpoint=bcf.v3.model.CommentViewpoint(guid=vp.guid),
        )
    ]


def generate_bcf_from_ifc_elements(
    ifc_file: ifcopenshell.file,
    ifc_file_path: str,
    error_dict: dict,
    output_bcf: str = "issues.bcfzip",
    author: str = "HVAC-Checker",
):
    """
    Generate a BCF file from a dictionary of IFC elements and template messages.

    elements_dict format:
        {
            "Issue Category 1": [
                {"element": element_id_or_instance, "message": "Custom message 1"},
                {"element": element_id_or_instance, "message": "Custom message 2"},
            ],
            "Issue Category 2": [
                ...
            ]
        }
    """
    extractor = IfcHeaderExtractor(ifc_file_path)
    header_info = extractor.extract()
    bcf_project = BcfXml.create_new(project_name=header_info.get("name"))
    bcf_project.save(filename=output_bcf, keep_open=True)
    bcf_zip = bcf_project._zip_file  # keep reference if needed

    for category, items in error_dict.items():
        for item in items:
            element = item["element"]
            if isinstance(element, int):
                element = ifc_file.by_id(element)
            add_bcf_issue(
                bcf_project=bcf_project,
                title=f"{category} - {element.GlobalId if hasattr(element, 'GlobalId') else 'Unknown'}",
                message=item.get("message", "No description provided"),
                author=author,
                elements=element,
            )

    bcf_project.save(filename=output_bcf)


def old_add_issue(
    bcf_obj: BcfXml,
    title: str,
    message: str,
    author: str,
    element: ifcopenshell.entity_instance,
    ifc_file: ifcopenshell.file,
    bcf_path: str,
    bcf_zip: bcf.v3.visinfo.ZipFileInterface,
) -> None:
    th = bcf_obj.add_topic(
        title,
        message,
        author,
        "Parameter Validation",
    )
    if isinstance(element, list):
        # inspect(element) # FOR DEBUGGING
        visinfo_handler = th.add_viewpoint(element[0])
        visinfo_handler.set_selected_elements(element)
    else:
        # inspect(element)
        visinfo_handler = th.add_viewpoint(element)
        visinfo_handler.set_selected_elements([element])

    camera_view_point, camera_direction, camera_up_vector = cameraSetup(
        element=element, ifc_file=ifc_file
    )
    visinfo_handler.visualization_info.perspective_camera = (
        bcf.v3.visinfo.build_camera_from_vectors(
            camera_position=camera_view_point,
            camera_dir=camera_direction,
            camera_up=camera_up_vector,
        )
    )
    # inspect(visinfo_handler) # FOR DEBUGGING

    th.comments = [
        bcf.v3.model.Comment(
            guid=str(uuid.uuid4()),
            date=iso_now(),
            author=author,
            comment=message,
            viewpoint=bcf.v3.model.CommentViewpoint(guid=visinfo_handler.guid),
        )
    ]


def old_generate_bcf_from_errors(
    console: Console,
    ifc_file: ifcopenshell.file,
    ifc_file_path: str,
    # misplacedElements: list,
    missingAHUsystems: dict,
    unassignedTerminals: dict,
    output_bcf: str = "hvac_issues.bcfzip",
) -> None:
    """
    Automatically writes a BCF file listing coordination issues:
      - misplacedElements: list of dicts with keys ['elementID', 'elementType', 'originalLevel', 'newLevel', ...]
      - missingAHUsystems: dict keyed by system name with ['ElementCount', 'ElementTypes', 'ElementIDs']
      - unassignedTerminals: dict keyed by flow direction, each containing list of GUIDs
    """

    console.print("🔧 Opening IFC file...")
    extractor = IfcHeaderExtractor(ifc_file_path)
    header_info = extractor.extract()
    console.print("📦 Creating new BCF project...")
    bcf_project = BcfXml.create_new(project_name=header_info.get("name"))
    bcf_project.save(filename=output_bcf, keep_open=True)
    bcf_zip = bcf_project._zip_file
    # # misplaced elements
    # console.print("🧱 Adding misplaced element topics...")
    # for error_category, elements in misplacedElements.items():
    #     for guid, e in elements.items():
    #         title = f"{error_category}: {e.get('elementType', 'Unknown')} representation issue - {guid}"
    #         desc_lines = [
    #             f"Element Type: {e.get('elementType', 'Unknown')}",
    #             f"Issue Category: {error_category}",
    #         ]
    #
    #         # Add more context if fields exist
    #         if "originalLevel" in e and "newLevel" in e:
    #             desc_lines.append(
    #                 f"Moved from {e['originalLevel']} (elev {e.get('originalLevelElevation')}) "
    #                 f"to {e['newLevel']} (elev {e.get('newLevelElevation')})."
    #             )
    #         if "minZ" in e and "maxZ" in e:
    #             desc_lines.append(
    #                 f"Min Z: {e['minZ']}, Max Z: {e['maxZ']}, Height: {e.get('elementHeight')}"
    #             )
    #
    #         desc = "\n".join(desc_lines)
    #
    #         old_add_issue(
    #             bcf_obj=bcf_project,
    #             title=title,
    #             message=desc,
    #             author="HVAC-Checker",
    #             element=ifc_file.by_id(guid),
    #             ifc_file=ifc_file,
    #             bcf_path=output_bcf,
    #             bcf_zip=bcf_zip,
    #         )

    # systems missing AHUs
    console.print("💨 Adding missing AHU system topics...")
    for sys_name, info in missingAHUsystems.items():
        title = f"IfcDistributionSystem - {sys_name}: Missing Air Handling Unit"
        desc = (
            f"The distribution system '{sys_name}' contains {info.get('ElementCount', 0)} elements "
            f"but no AHU (IfcUnitaryUnit) was found.\n"
            f"Types: {info.get('ElementTypes', 'Unknown')}."
        )

        # this one does not work, and needs to be fixed!!!!!!
        # inspect(info)
        systemElements = [ifc_file.by_id(el) for el in info["ElementIDs"]]

        if systemElements:
            old_add_issue(
                bcf_obj=bcf_project,
                title=title,
                message=desc,
                author="HVAC-Checker",
                element=systemElements,
                ifc_file=ifc_file,
                bcf_path=output_bcf,
                bcf_zip=bcf_zip,
            )
            # viewpoint.save()

    # unassigned air terminals
    console.print("🌬️ Adding unassigned terminal topics...")
    for flow_dir, element_list in unassignedTerminals.items():
        for element in element_list:
            title = f"Air terminal not placed inside a space - ({element})"
            desc = f"Air terminal {element} - {flow_dir} is not located inside an IfcSpace."

            old_add_issue(
                bcf_obj=bcf_project,
                title=title,
                message=desc,
                author="HVAC-Checker",
                element=ifc_file.by_id(element),
                ifc_file=ifc_file,
                bcf_path=output_bcf,
                bcf_zip=bcf_zip,
            )

    # save the BCF file
    bcf_project.save(filename=output_bcf)
    console.print(f"✅ BCF file successfully written: {output_bcf}")
