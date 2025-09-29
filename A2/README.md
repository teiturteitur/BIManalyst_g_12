# BIManalyst group 12

A2a: About your group

FOCUS AREA: INDOOR AND ENERGY

ROLE: Analysts

We agree (3) that we are confident in coding in python

A2b: Identify Claim

The claim we are checking:

CHECKING FREE HEIGHTS OF ALL STOREYS

CLAIM: Ceiling heights of at least 2.6m
REPORT: D_ClientReport_Team16
PAGE: 7

A2c: Use Case
How you would check this claim?

Method (automatic)

The claim is that ceiling heights (free height from floor to lowest element) must be ≥ 2.6 m.

The workflow is automated using IfcOpenShell:

Sanity check (ElementLeveler): Verify that all elements are assigned to the correct building storey. Vertical elements are moved to the building level. If not correct, they are reassigned with ifcopenshell.api.spatial.assign_container.

Free height check (FreeHeightChecker): For each storey, calculate the free height as the lowest Z-coordinate of the element minus the storey elevation. Identify the lowest element per storey, compare with the 2.6 m threshold, and color the element red (fail) or yellow (pass).

Outputs: Updated IFC file (with corrected assignments and colors) and a summary report showing minimum free height per storey.

When would this claim need to be checked?

During the design phase, whenever the model is updated (e.g. new MEP elements, layout changes).

At design freeze before handover to the client.

Optionally in the build phase, for as-built verification.

What information does this claim rely on?

IFC model with:

Defined IfcBuildingStorey entities with correct elevations.

Relevant MEP elements (e.g. IfcDuctSegment, IfcAirTerminal).

Geometric data available for ifcopenshell.geom to extract global Z-coordinates.

Units must be in meters, with USE_WORLD_COORDS=True.

The threshold value (2.6 m, configurable).

What phase? planning, design, build or operation.

Mainly Design, secondarily Build.

What BIM purpose is required? Gather, generate, analyse, communicate or realise?

Analyse: Calculate free heights and detect non-compliance.

Communicate: Provide visual IFC feedback (colored elements) and summary reports.


Produce a BPMN drawing for your chosen use case. link to this so we can see it in your markdown file. To do this you will have to save it as an SVG, please also save the BPMN with it.mYou can use this online tool to create a BPMN file.














