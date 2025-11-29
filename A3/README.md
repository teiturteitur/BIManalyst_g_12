<h1 align='center'> A3 - VENTILATION ANALYSIS TOOL - GROUP 10

> by Group 10 - ADVANCED BIM E25
> s214310, s203493, s201348

### Introduction and Goal

This tool aims to be used in the early design phases of HVAC modelling - catching possible errors or oversights made during this design phase.

The tool consists of three main modules that all work independently, so feel free to replace these as needed :)

Here's a brief explanation of the modules:

1. AirflowEstimator.py
    This module estimates airflows for all spaces present in a given IFC file (i.e. an ARCH IFC-file from the Advanced Building Design (41936) course available at DTU).

    The air flows are estimated using the IEQ categories presented in the DS_EN 16798-1:2019 international standard.

    Occupancy is estimated in a couple of ways, according to what data is available in the given IFC file. So in principle, the script performs the following checks and calculates the occupancy accordingly:
        - If occupancy is assigned as a PSET, use it.
        - If theres no available PSET, count the amount of chairs in the space and use the number of chairs as design occupancy.
        - If theres no available PSET and no chairs, use an estimated occupant density (pers./m^2) according to the _space.LongName_ or a backup occupant density. (Backup occupant densitites are from Appendix B in the aforementioned standard)

    If the spaces in the given IFC file does not have the following PSETS, they are added and the new analyzed file is saved IFC-file is saved (in OutputFiles).


2. VentilationSystemAnalyzer.py
    Quite a lot is happening in this module. But we'll try to make it short :) 
    
    This module aims to analyze all present ventilation systems in a given IFC file and cross-referencing them with the spaces in a matching IFC-file containing spaces (i.e. a MEP and an ARCH IFC-file from the Advanced Building Design (41936) course available at DTU).

    A number of checks are performed, if an element or a system does not pass, the analysis for this element/system does NOT continue and the elements are saved in dictionaries, for BCF generation (but we'll get to that ;) ).

    These are the checks performed:

    1. Does an element have an AHU assigned? 
        If not, the entire system is saved in the _missingAHUsystems_ dictionary.

        If a system contains an AHU, the supply/return systems are paired (by checking if the AHU.globalID exists in multiple systems) - and the analysis continues!

    2. For all systems containing AHUs, clash detection is performed of the air terminals in the system and the spaces from the matching IFC-file. 
        If an air terminal is NOT inside a space, they are saved in the _unassignedTerminals_ dictionary.

        If an air terminal IS inside a space, the analysis continues!

    For all air terminals that have passed these checks, the following steps in the analysis are performed:

    3. For all air terminals in each space (with air terminals) divide the required air flow (from the space PSETs) to the present air terminals.
    
    4. For visualization purposes, data trees are built to show how the air flow branches out in the analysed ventilation systems.

    5. LAST STEP! Now that the air flow is estimated in all elements in the system, the pressure loss can be calculated. 
        For duct elements, the pressure loss is found by calculating the hydraulic diameter (according to if the duct is rectangular or round).

        For duct fittings it gets a bit trickier, as they can be a long list of different types of fittings, i.e. duct expansions, bends, T-, and X-fittings.
        The pressure loss calculations have not been implemented for all fitting types. The ground work has been made, to determine the type of fitting and its IfcDistributionPorts.

3. BcfGenerator.py
    This module creates BCF-files for IFC-files from dictionaries with IfcElements (the ones from the previous modules).

    All BCF issues are created with camera views and descriptions assigned to them.


### USAGE

To use this tool, add IFC-file pairs to the ifcFiles directory and then run one of the two main.py files.

1. CLI_main.py
    This file contains a command line UI (CLI) where the user is able to choose the analysed files, the IEQ category and view the analysis results. The user is also able to export the generated BCF- and IFC-files. 

2. main.py
    This file contains a more strict pipeline, more aimed towards automated use. As of now, the user still needs to input a choice of which file pairs are analysed, but this can easily be excluded for a more automated use case. 


### FUTURE WORK

- Pressure loss estimation of duct fittings and air terminals
- Compatability with different IFC-file types. 
