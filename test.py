
import ifcopenshell.util.element as util
import os
import ifcopenshell
import ifcopenshell.util.file
import ifcopenshell.guid
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from ifcopenshell.util.file import IfcHeaderExtractor

console = Console()


# extractor = IfcHeaderExtractor('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-01-D-ARCH.ifc')
# extractor = IfcHeaderExtractor('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-08-D-MEP.ifc')
extractor = IfcHeaderExtractor('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-10-D-ARCH.ifc')
# extractor = IfcHeaderExtractor('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/ifcFiles/25-10-D-MEP.ifc')
# extractor = IfcHeaderExtractor('/Users/teiturheinesen/Documents/DTU/Advanced BIM/ApocalypseBIM/outputFiles/ElementLeveler_withSpaces.ifc')
# Get dictionary of the extracted metadata.
header_info = extractor.extract()

# Print the extracted information
# console.print(header_info)
# ViewDefinition[DesignTransferView]
# console.print("File Description:", header_info.get("description"))



# 2;1
# console.print("Implementation Level:", header_info.get("implementation_level"))

# file.ifc
console.print("File Name:", header_info.get("name"))

# 2024-06-25T15:48:10+05:00
# console.print("Time Stamp:", header_info.get("time_stamp"))

# IFC4X3_ADD2
# console.print("Schema Name:", header_info.get("schema_name"))
