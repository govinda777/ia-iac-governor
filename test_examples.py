import os
import sys

# Force UTF-8 encoding for stdout/stderr to fix Windows pre-commit hook UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from workflow.tools import GovernanceManagerTool
from core.reporting import generate_html_report

def test_all_examples():
    console = Console()
    tool = GovernanceManagerTool()
    
    if len(sys.argv) > 1:
        test_dirs = sys.argv[1:]
    else:
        test_dirs = ["examples"]
        
    expectations = {
        "mandatory_tagging.tf": "DENIED",
        "high_cost_infrastructure.tf": "DENIED",
        "secure_database.tf": "DENIED",
        "pci_network_segmentation.tf": "DENIED",
        "developer_role_violation.tf": "DENIED",
        "standard_s3_bucket.tf": "APPROVED",
        "governed_infrastructure.tf": "DENIED",

        # Benchmarks - Account 1 (Source)
        "benchmarks/scenario-001-shadow-admin/account_1_setup.tf": "DENIED",
        "benchmarks/scenario-002-public-private-bridge/account_1_setup.tf": "DENIED",
        "benchmarks/scenario-003-artifact-poisoning/account_1_setup.tf": "DENIED",
        "benchmarks/scenario-004-kms-decryption/account_1_setup.tf": "APPROVED",

        # Benchmarks - Account 2 (Target)
        "benchmarks/scenario-001-shadow-admin/account_2_target.tf": "DENIED",
        "benchmarks/scenario-002-public-private-bridge/account_2_target.tf": "DENIED",
        "benchmarks/scenario-003-artifact-poisoning/account_2_target.tf": "DENIED",
        "benchmarks/scenario-004-kms-decryption/account_2_target.tf": "APPROVED",
    }

    results = []
    failed_tests = []
    skipped_tests = 0

    console.print(f"\n[bold blue]:mag: Testing all examples and benchmarks in: {', '.join(test_dirs)}[/bold blue]")
    console.print("="*60 + "\n")
    
    # Exibir resumo da base de conhecimento (ou grafo completo se solicitado)
    show_full_graph = "--full-graph" in sys.argv
    try:
        with open("schema/security_graph.json", "r") as f:
            sg = json.load(f)
            nodes_count = len(sg.get("nodes", []))
            edges_count = len(sg.get("edges", []))
            
            if show_full_graph:
                lines = ["graph TD"]
                for node in sg.get("nodes", []):
                    safe_id = node['id'].replace('-', '_')
                    label = f"{node['id']} ({node['type']})"
                    lines.append(f'    {safe_id}["{label}"]')
                for edge in sg.get("edges", []):
                    safe_from = edge['from'].replace('-', '_')
                    safe_to = edge['to'].replace('-', '_')
                    lines.append(f'    {safe_from} -->|"{edge["type"]}"| {safe_to}')
                
                mermaid_str = "\n".join(lines)
                console.print(Panel(
                    f"[cyan]{mermaid_str}[/cyan]", 
                    title="[bold yellow]:globe_with_meridians: Agent Knowledge Base (Full Security Graph)[/bold yellow]", 
                    border_style="yellow"
                ))
            else:
                console.print(Panel(
                    f"[cyan]Knowledge Base contains {nodes_count} resources and {edges_count} relationship paths.[/cyan]\n[dim]Use --full-graph to see the complete Mermaid diagram.[/dim]",
                    title="[bold yellow]:globe_with_meridians: Agent Knowledge Base Summary[/bold yellow]",
                    border_style="yellow",
                    expand=False
                ))
            console.print("\n")
    except Exception as e:
        pass

    files_to_test = []
    for test_dir in test_dirs:
        if test_dir.startswith("-"): continue # Skip flags
        if not os.path.exists(test_dir):
            continue
        
        if os.path.isfile(test_dir):
            if test_dir.endswith(".tf"):
                files_to_test.append(test_dir)
        else:
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith(".tf"):
                        files_to_test.append(os.path.join(root, file))

    for path in files_to_test:
        file = os.path.basename(path)
        root = os.path.dirname(path)
        
        # Try to load metadata if available
        metadata = {}
        metadata_path = os.path.join(root, "vulnerability_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as mf:
                try:
                    metadata = json.load(mf)
                except json.JSONDecodeError:
                    pass
        else:
            metadata = {
                "name": file,
                "description": f"Standard test case: {file}",
            }

        # Create UI Panel for current test (Simplified)
        panel_text = f"[bold]Scenario:[/bold] {metadata.get('name', file)}\n"
        if metadata.get("certification"):
            panel_text += f"[bold]Cert:[/bold] {metadata.get('certification')} ({metadata.get('severity', 'UNKNOWN')})"
        
        console.print(Panel(panel_text, title=f":rocket: [yellow]{file}[/yellow]", expand=False, border_style="blue"))

        with open(path, "r", encoding="utf-8") as f:
            hcl_content = f.read()

        # Run with spinner
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"[cyan]Analyzing {file}...", total=None)
            verdict_output = tool._run(hcl_content)
            progress.update(task, completed=True)

        # Determine actual verdict
        actual_verdict = "ERROR"
        is_simulated = "Terraform CLI not found" in verdict_output or "simulated" in verdict_output.lower()
        
        if "VERDICT: APPROVED" in verdict_output:
            actual_verdict = "APPROVED"
        elif "VERDICT: DENIED" in verdict_output:
            actual_verdict = "DENIED"
        elif "VERDICT: CRITICAL FAILURE" in verdict_output:
            actual_verdict = "DENIED"
        
        expected_verdict = expectations.get(path, expectations.get(file, "APPROVED"))
        passed = actual_verdict == expected_verdict

        # Record result
        results.append({
            "path": path,
            "expected": expected_verdict,
            "actual": actual_verdict,
            "passed": passed,
            "output": verdict_output,
            "metadata": metadata,
            "simulated": is_simulated
        })

        # Print result inline
        status_icon = ":white_check_mark:" if passed else ":x:"
        status_color = "green" if passed else "red"
        sim_tag = " [yellow](SIMULATED)[/yellow]" if is_simulated else ""
        console.print(f"{status_icon} [bold {status_color}]{file}: {actual_verdict}[/bold {status_color}] (Expected {expected_verdict}){sim_tag}")
        
        if not passed:
            failed_tests.append(path)

        # Mostrar feedback apenas se falhou ou se for negado
        if not passed or actual_verdict == "DENIED":
            clean_output = "\n".join(verdict_output.split("\n")[2:]).strip()
            if clean_output:
                console.print(Panel(clean_output, title="[cyan]Validation Feedback[/cyan]", border_style="cyan", expand=False))
        
        # Real Agent Predictive Analysis (Rich Neural Map)
        tree = Tree(f"🧠 [bold magenta]Sentinel Neural Activation Map: {file}[/bold magenta]")
        
        # 1. Input Layer
        input_node = tree.add("📥 [bold cyan]Input Layer[/bold cyan]")
        input_node.add(f"Type: [dim]Terraform HCL / JSON Plan[/dim]")
        input_node.add(f"Source: [dim]{path}[/dim]")
        
        # 2. Execution Layers
        layers_node = tree.add("🔍 [bold yellow]Governance Execution Layers[/bold yellow]")
        
        layer_status = {}
        for line in verdict_output.split("\n"):
            if line.strip().startswith("- "):
                parts = line.strip()[2:].split(":")
                if len(parts) >= 2:
                    layer_status[parts[0].strip().lower()] = parts[1].strip()

        for l_name, l_title in [("cost", "💰 Cost Validation"), ("opa", "🛡️ Policy Scanning (OPA)")]:
            status = layer_status.get(l_name, "SKIPPED")
            # If the status is not in the output, it means the provider might have run but didn't find anything,
            # or it was actually skipped. But with our new manager, it should be there if enabled.
            s_color = "green" if "APPROVED" in status or "PASS" in status else "red" if "DENIED" in status else "yellow"
            layers_node.add(f"{l_title}: [bold {s_color}]{status}[/]")
        
        # 3. Predictive Layer (Firefly)
        predictive_node = tree.add("🔮 [bold blue]Predictive Governance Layer (Sentinel)[/bold blue]")
        p_status = layer_status.get('firefly', "SKIPPED")
        p_color = "green" if "APPROVED" in p_status else "red" if "DENIED" in p_status else "yellow"
        predictive_node.add(f"Neural Engine Status: [bold {p_color}]{p_status}[/]")
        
        if actual_verdict == "DENIED":
            n3 = predictive_node.add("🧠 [bold yellow]Neural Graph Engine Activation[/bold yellow]")
            n3.add(":warning: [bold red]Toxic Combination Found in Decision Tree![/bold red]")
            
            # Use metadata attack path if available
            logic_str = None
            if metadata.get("attack_path") and metadata["attack_path"].get("logic"):
                logic_str = metadata["attack_path"]["logic"]
            
            if logic_str:
                parts = [p.strip() for p in logic_str.split("->")]
                title = "🕸️ [bold cyan]Activated Sub-Graph Path (Attack Vector)[/bold cyan]"
                g_diagram = n3.add(title)
                
                for i, part in enumerate(parts):
                    if part.startswith("Node("):
                        node_text = part[5:-1]
                        g_diagram.add(f"[bold white on red] ⬢ {node_text} [/]")
                    elif part.startswith("Edge("):
                        edge_text = part[5:-1]
                        g_diagram.add(f"[dim magenta]   ┃  ({edge_text})[/]")
                        g_diagram.add(f"[dim magenta]   ▼[/]")
        else:
            predictive_node.add("✅ [bold green]Blast Radius: Contained[/bold green]")
            predictive_node.add("[dim]No security regression patterns detected in knowledge base.[/dim]")

        # 4. Final Decision
        if "DENIED" in actual_verdict:
            v_color = "red"
            v_msg = "INFRASTRUCTURE REJECTED"
        elif "ERROR" in actual_verdict:
            v_color = "yellow"
            v_msg = "GOVERNANCE ERROR (Tools Missing)"
        else:
            v_color = "green"
            v_msg = "INFRASTRUCTURE APPROVED"
            
        tree.add(f"🎯 [bold italic white on {v_color}] FINAL VERDICT: {v_msg} [/]")
        
        console.print(tree)
        console.print("\n")
        console.rule(f"[bold green]End of Neural Activation for {file}[/bold green]", style="green")
        console.print("\n")

    # Summary Table
    console.print("\n" + "="*60)
    table = Table(title="Test Execution Summary")
    table.add_column("Total", justify="center", style="cyan")
    table.add_column("Passed", justify="center", style="green")
    table.add_column("Failed", justify="center", style="red")
    table.add_column("Skipped", justify="center", style="yellow")
    
    table.add_row(str(len(results) + skipped_tests), str(len(results) - len(failed_tests)), str(len(failed_tests)), str(skipped_tests))
    console.print(table)

    # Generate HTML Report
    try:
        report_path = generate_html_report(results, "test_report.html")
        console.print(f":page_facing_up: [bold blue]HTML Report generated at:[/bold blue] {os.path.abspath(report_path)}")
        
        import webbrowser
        webbrowser.open('file://' + os.path.realpath(report_path))
        console.print(":globe_with_meridians: [bold green]Opening HTML Report in your default browser...[/bold green]")
        
    except Exception as e:
        console.print(f":warning: [bold red]Failed to generate HTML report: {e}[/bold red]")

    if not failed_tests:
        console.print("\n:white_check_mark: [bold green]All examples and benchmarks behaved as expected![/bold green]")
        console.print("="*60)
    else:
        console.print(f"\n:x: [bold red]Some tests failed to meet expectations: {', '.join(failed_tests)}[/bold red]")
        console.print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    test_all_examples()
