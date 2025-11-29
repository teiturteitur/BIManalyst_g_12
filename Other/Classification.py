import ifcopenshell
import ifcopenshell.util.classification

model = ifcopenshell.open("/Users/teiturheinesen/Library/CloudStorage/OneDrive-SharedLibraries-DanmarksTekniskeUniversitet/Rasmus Niss Kloppenborg - IFC modeller/25-16-D-MEP.ifc")


classifications = model.by_type("IfcClassification")
print("Classifications:", classifications)

element = model.by_type("IfcDuctSegment")[0]


references = ifcopenshell.util.classification.get_references(element)
for reference in references:
    system = ifcopenshell.util.classification.get_classification(reference)
    print("This reference is part of the system", system.Name)
    print("The element has a classification reference of", reference.Identification)
if not references:
    print("No classification references found for the element")