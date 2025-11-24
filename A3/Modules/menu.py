import ifcopenshell
import rich
from rich import table
from rich.console import Console
from .setupFunctions import choose_ifc_pair_from_directory, choose_ifcElementType
from .AirFlowEstimator import *
from .VentilationSystemAnalyzer import *
from .BcfGenerator import *
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm


def menuFilePicker(console):
    # ask user to choose IFC file pair from directory

    ifc_filePath, ifc_SpacePath = choose_ifc_pair_from_directory(
        console=console, directory="A3/ifcFiles", extension=".ifc"
    )

    if ifc_filePath != None:
        # console.print(ifc_filePath)
        ifc_file = ifcopenshell.open(ifc_filePath)

    else:
        ifc_file = None
    space_file_beforeCheck = ifcopenshell.open(ifc_SpacePath)

    return ifc_filePath or None, ifc_file or None, space_file_beforeCheck


def menuIFCAnalysis(
    console: Console, MEP_file: ifcopenshell.file | None, Space_file: ifcopenshell.file
):
    ifc_file_Spaces, table_airflows = spaceAirFlowCalculator(
        console=console, space_file=Space_file
    )

    if MEP_file:
        # space and MEP file

        # define target elements
        targetElements, targetElementTable = choose_ifcElementType(
            console=console, ifcFile=MEP_file, category="MEP-HVAC"
        )
        with console.status(
            status="Finding ventilation systems with AHUs...", spinner="dots"
        ):
            identifiedSystems, missingAHUsystems, table_AHUs = ahuFinder(
                console=console,
                ifc_file=MEP_file,
                targetSystems="IfcDistributionSystem",
            )

        with console.status(
            status="Connecting air terminals with spaces...", spinner="dots"
        ):
            spaceTerminals, unassignedTerminals, table_Spaces = (
                airTerminalSpaceClashAnalyzer(
                    console=console,
                    MEP_file=MEP_file,
                    space_file=ifc_file_Spaces,
                    identifiedSystems=identifiedSystems,
                    space_file_name="25-10-D-ARCH.ifc",
                )
            )

        with console.status(
            status="Assigning air flows and pressure losses to air terminals..."
        ):
            systemsTree, ifc_file_new = getSystemTrees(
                console=console,
                identifiedSystems=identifiedSystems,
                ifc_file=MEP_file,
                space_file=ifc_file_Spaces,
                spaceTerminals=spaceTerminals,
                showChoice="n",
            )

        return (
            ifc_file_Spaces,
            table_airflows,
            targetElements,
            targetElementTable,
            identifiedSystems,
            missingAHUsystems,
            table_AHUs,
            spaceTerminals,
            unassignedTerminals,
            table_Spaces,
            systemsTree,
            ifc_file_new,
        )

    else:
        # only space file
        return ifc_file_Spaces, table_airflows


def menuGenerateFiles(
    console,
    new_SpaceFile,
    new_MEPFile,
    MEP_file_path,
    missingAHUsystems,
    unassignedTerminals,
):
    with console.status(status="Generating BCF-file...", spinner="dots"):
        old_generate_bcf_from_errors(
            console=console,
            ifc_file=new_MEPFile,
            ifc_file_path=MEP_file_path,
            missingAHUsystems=missingAHUsystems,
            unassignedTerminals=unassignedTerminals,
            output_bcf="A3/outputFiles/HVAC_Issues.bcfzip",
        )
    with console.status(status="Generating new IFC files...", spinner="dots"):
        new_MEPFile.write(f"A3/outputFiles/Analyzed_MEP_File.ifc")
        new_SpaceFile.write(f"A3/outputFiles/Analyzed_Space_File.ifc")

    console.print("Done!")


def bigMenu(console):
    # internal state
    MEP_path = None
    ARCH_path = None
    MEP_file = None
    ARCH_file = None

    # results / analysis state
    analysis_results = None
    generated_files = False
    targetElements = None  # NEW: stored for status bar
    analysis_results = None
    ifc_file_Spaces = None
    table_airflows = None
    targetElements = None
    identifiedSystems = None
    missingAHUsystems = None
    table_AHUs = None
    spaceTerminals = None
    unassignedTerminals = None
    table_Spaces = None
    systemsTree = None
    ifc_file_new = None
    targetElementTable = None

    while True:
        console.clear()
        console.print("\n")

        # -------------------------
        # STATUS PANEL
        # -------------------------
        status_table = Table.grid(padding=1)
        status_table.add_column(justify="left")
        status_table.add_column(justify="right")

        mep_loaded = "[green]✔[/green]" if MEP_file else "[red]✘[/red]"
        arch_loaded = "[green]✔[/green]" if ARCH_file else "[red]✘[/red]"
        analysis_done = "[green]✔[/green]" if analysis_results else "[red]✘[/red]"
        export_done = "[green]✔[/green]" if generated_files else "[red]✘[/red]"

        # if targetElementTable:
        #     status_table.add_row("MEP Target Elements:", "")
        #     status_table.add_row("", Panel(targetElementTable, border_style="blue"))
        #
        # else:
        #     status_table.add_row("Target Elements:", "[red]None[/red]")

        status_table.add_row("MEP file loaded:", mep_loaded)
        status_table.add_row("ARCH file loaded:", arch_loaded)
        status_table.add_row("Analysis results:", analysis_done)
        status_table.add_row("Export done:", export_done)

        console.print(
            Panel(
                status_table,
                title="[bold yellow]STATUS[/bold yellow]",
                border_style="cyan",
                expand=False,
            )
        )

        # -------------------------
        # MAIN MENU
        # -------------------------
        console.print(
            Panel.fit(
                "[bold magenta]⭐ IFC HVAC SYSTEM ANALYZER ⭐[/bold magenta]\n"
                "[green]Advanced BIM - E25[/green]",
                title="[bold yellow]BIManalyst TOOL[/bold yellow]",
                subtitle="by Group 12",
                border_style="cyan",
            )
        )

        console.print("\n[bold cyan]MENU OPTIONS[/bold cyan]")
        console.print("1. Select New Files")
        console.print("2. Run Available Analysis")
        console.print("3. Show Results")
        console.print("4. Export IFC and BCF Files")
        console.print("q. Quit\n")

        choice = Prompt.ask("[bold white]Choose an option[/bold white]")

        # -----------------------------------------------------
        # 1 — SELECT NEW FILES
        # -----------------------------------------------------
        if choice == "1":
            console.print("\n[cyan]Selecting files...[/cyan]")
            filePathMEP, MEP_file_new, ARCH_file_new = menuFilePicker(console)
            MEP_path = filePathMEP
            MEP_file = MEP_file_new
            ARCH_file = ARCH_file_new

            # reset states
            analysis_results = None
            generated_files = False
            targetElementTable = None

            console.print("[green]Files loaded successfully![/green]")

        # -----------------------------------------------------
        # 2 — RUN ANALYSIS
        # -----------------------------------------------------
        elif choice == "2":
            if not ARCH_file:
                console.print("[red]You must load files first.[/red]")
                continue

            console.print("[cyan]Running analysis...[/cyan]")
            result = menuIFCAnalysis(console, MEP_file, ARCH_file)

            # unpack based on whether MEP was provided
            if MEP_file is None:
                # ARCH ONLY RUN
                analysis_results = result
            else:
                (
                    ifc_file_Spaces,
                    table_airflows,
                    targetElements,
                    targetElementTable,
                    identifiedSystems,
                    missingAHUsystems,
                    table_AHUs,
                    spaceTerminals,
                    unassignedTerminals,
                    table_Spaces,
                    systemsTree,
                    ifc_file_new,
                ) = result

                analysis_results = result
                targetElementTable = (
                    targetElements[1] if isinstance(targetElements, tuple) else None
                )

            console.print("[green]Analysis completed![/green]")
            console.input("Press Enter to continue...")

        # -----------------------------------------------------
        # 3 — SHOW RESULTS (UNDERMENU WITH LOOP)
        # -----------------------------------------------------

        elif choice == "3":
            if not analysis_results:
                console.print("[red]No analysis results available.[/red]")
                continue

            elif len(analysis_results) == 2:
                # ARCH only
                (
                    ifc_file_Spaces,
                    table_airflows,
                ) = analysis_results
                console.print("\n[cyan]Space airflow table:[/cyan]")
                console.print(table_airflows)
                console.input("Press Enter to continue...")
                continue
            else:
                (
                    ifc_file_Spaces,
                    table_airflows,
                    targetElements,
                    targetElementTable,
                    identifiedSystems,
                    missingAHUsystems,
                    table_AHUs,
                    spaceTerminals,
                    unassignedTerminals,
                    table_Spaces,
                    systemsTree,
                    ifc_file_new,
                ) = analysis_results

            # Build dynamic menu options
            results_menu = []  # list of (key, label, callable)

            if table_airflows:
                results_menu.append(
                    ("1", "Air Flow Table", lambda: console.print(table_airflows))
                )
            if table_AHUs:
                results_menu.append(
                    ("2", "AHU Table", lambda: console.print(table_AHUs))
                )
            if table_Spaces:
                results_menu.append(
                    ("3", "Space Assignment Table", lambda: console.print(table_Spaces))
                )
            if missingAHUsystems:
                results_menu.append(
                    ("4", "Missing AHUs", lambda: console.print(missingAHUsystems))
                )
            if unassignedTerminals:
                results_menu.append(
                    (
                        "5",
                        "Unassigned Terminals",
                        lambda: console.print(unassignedTerminals),
                    )
                )
            if systemsTree:
                results_menu.append(
                    ("6", "System Trees", lambda: systemsTreeMenu(console, systemsTree))
                )
            if targetElementTable:
                results_menu.append(
                    (
                        "7",
                        "Target Element Table",
                        lambda: console.print(targetElementTable),
                    )
                )

            # Loop submenu
            while True:
                console.print("\n[bold cyan]RESULTS MENU[/bold cyan]")
                for key, label, _ in results_menu:
                    console.print(f"{key}. {label}")
                console.print("b. Back\n")

                sub_choice = Prompt.ask("Choose option")

                if sub_choice == "b":
                    break

                # Run selected action
                for key, label, action in results_menu:
                    if key == sub_choice:
                        action()
                        break
                else:
                    console.print("[red]Invalid choice.[/red]")

                # console.input("\nPress Enter to continue...")

        # -----------------------------------------------------
        # 4 — EXPORT IFC + BCF
        # -----------------------------------------------------
        elif choice == "4":
            if not analysis_results:
                console.print("[red]Run analysis before exporting files.[/red]")
                continue

            (
                ifc_file_Spaces,
                table_airflows,
                targetElements,
                targetElementTable,
                identifiedSystems,
                missingAHUsystems,
                table_AHUs,
                spaceTerminals,
                unassignedTerminals,
                table_Spaces,
                systemsTree,
                ifc_file_new,
            ) = analysis_results

            console.print("[cyan]Generating files...[/cyan]")

            menuGenerateFiles(
                console=console,
                new_SpaceFile=ifc_file_Spaces,
                new_MEPFile=ifc_file_new,
                MEP_file_path=MEP_path,
                missingAHUsystems=missingAHUsystems,
                unassignedTerminals=unassignedTerminals,
            )

            generated_files = True
            console.print("[green]BCF & IFC export complete![/green]")
            console.input("Press Enter to continue...")

        # -----------------------------------------------------
        # QUIT
        # -----------------------------------------------------
        elif choice.lower() == "q":
            console.print("[bold green]Goodbye![/bold green]\n")
            break

        else:
            console.print("[red]Invalid choice.[/red]")


def systemsTreeMenu(console, systemsTree):
    # If the result is a single Tree object, wrap it in a dictionary
    if hasattr(systemsTree, "show") and not isinstance(systemsTree, dict):
        systemsTree = {"System": systemsTree}

    while True:
        console.print("\n[cyan]Select system tree:[/cyan]")
        #
        keys = list(systemsTree.keys())

        sysname = keys[0]
        tree_obj = systemsTree[sysname]

        propChoice = Prompt.ask(
            "Select property",
            choices=["airFlow", "pathPressureLoss", "elementPressureLoss", "b"],
            default="airFlow",
            case_sensitive=False,
        )

        if propChoice == "b":
            break
        try:
            tree_obj.show(
                idhidden=False, data_property=propChoice, line_type="ascii-em"
            )
        except Exception as e:
            console.print(f"[red]Could not display tree: {e}[/red]")
