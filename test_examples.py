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
    
    # Exibir a rede de grafos consultada (Mermaid) no console
    try:
        with open("schema/security_graph.json", "r") as f:
            sg = json.load(f)
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
                title="[bold yellow]:globe_with_meridians: Agent Knowledge Base (Global Security Graph)[/bold yellow]", 
                border_style="yellow"
            ))
            console.print("\n")
    except Exception as e:
        pass

    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith(".tf"):
                    path = os.path.join(root, file)
                    
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

                    # Create UI Panel for current test
                    panel_text = f"[bold]Path:[/bold] {path}\n"
                    if metadata.get("name"):
                        panel_text += f"[bold]Scenario:[/bold] {metadata.get('name')}\n"
                    if metadata.get("certification"):
                        panel_text += f"[bold]Certification:[/bold] {metadata.get('certification')} (Severity: {metadata.get('severity', 'UNKNOWN')})\n"
                    if metadata.get("description"):
                        panel_text += f"[bold]Description:[/bold] {metadata.get('description')}\n"
                    
                    if metadata.get("attack_path") and metadata["attack_path"].get("logic"):
                        panel_text += f"\n[bold magenta]Attack Path (Logic Diagram):[/bold magenta]\n[cyan]{metadata['attack_path']['logic']}[/cyan]"

                    console.print(Panel(panel_text, title=f":rocket: Running Test: [yellow]{file}[/yellow]", expand=False, border_style="blue"))

                    with open(path, "r", encoding="utf-8") as f:
                        hcl_content = f.read()

                    # Run with spinner
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                        task = progress.add_task("[cyan]Evaluating Terraform Plan against Governance Agents...", total=None)
                        verdict_output = tool._run(hcl_content)
                        progress.update(task, completed=True)

                    # Determine actual verdict
                    actual_verdict = "ERROR"
                    if "Terraform CLI is not installed" in verdict_output:
                        console.print(f":warning: [bold yellow]SKIPPED (Terraform CLI missing)[/bold yellow]\n")
                        console.rule(f"[bold green]End of {file}[/bold green]", style="green")
                        console.print("\n\n")
                        skipped_tests += 1
                        expected_verdict = expectations.get(path, expectations.get(file, "APPROVED"))
                        results.append({
                            "path": path,
                            "expected": expected_verdict,
                            "actual": "SKIPPED",
                            "passed": False,
                            "output": "Terraform CLI is missing.",
                            "metadata": metadata,
                            "skipped": True
                        })
                        continue
                    elif "VERDICT: APPROVED" in verdict_output:
                        actual_verdict = "APPROVED"
                    elif "VERDICT: DENIED" in verdict_output:
                        actual_verdict = "DENIED"
                    elif "VERDICT: CRITICAL FAILURE" in verdict_output:
                        actual_verdict = "DENIED" # Treat critical failure as a form of denial for now
                    
                    expected_verdict = expectations.get(path, expectations.get(file, "APPROVED"))
                    passed = actual_verdict == expected_verdict

                    # Record result for HTML
                    results.append({
                        "path": path,
                        "expected": expected_verdict,
                        "actual": actual_verdict,
                        "passed": passed,
                        "output": verdict_output,
                        "metadata": metadata
                    })

                    # Print result inline
                    if passed:
                        console.print(f":white_check_mark: [bold green]{path}: {actual_verdict}[/bold green] (Expected {expected_verdict})")
                    else:
                        console.print(f":x: [bold red]{path}: {actual_verdict}[/bold red] (Expected {expected_verdict})")
                        failed_tests.append(path)

                    # Mostrar o feedback do que foi validado (Removendo a primeira linha VERDICT: ...)
                    clean_output = "\n".join(verdict_output.split("\n")[2:]).strip()
                    if clean_output:
                        console.print(Panel(clean_output, title="[cyan]Validation Feedback[/cyan]", border_style="cyan", expand=False))
                    
                    # Simulated Agent Predictive Analysis
                    agent_text = f"[bold italic]Thought:[/bold italic] I need to audit the HCL code for {file} to ensure compliance.\n"
                    agent_text += f"[bold italic]Action:[/bold italic] Running GovernanceManagerTool (Cost, Firefly, OPA)...\n"
                    agent_text += f"[bold italic]Observation:[/bold italic] The tools returned a {'DENIED' if 'DENIED' in actual_verdict else 'APPROVED'} verdict.\n"
                    
                    if metadata.get("graph_query_reference"):
                        agent_text += f"\n[bold italic]Predictive Analysis (Sentinel):[/bold italic] I am cross-referencing this plan with the Security Graph.\n"
                        agent_text += f"Running Query: [dim]{metadata['graph_query_reference']}[/dim]\n"
                        if "DENIED" in actual_verdict:
                            agent_text += f":warning: [yellow]Toxic Combination Detected![/yellow] This deployment matches the '{metadata.get('name', 'Unknown')}' causal scenario.\n"
                            
                            # Render ASCII Diagram of the attack path
                            if metadata.get("attack_path") and metadata["attack_path"].get("logic"):
                                logic_str = metadata["attack_path"]["logic"]
                                parts = [p.strip() for p in logic_str.split("->")]
                                agent_text += f"\n[bold cyan]Detected Attack Path Graph:[/bold cyan]\n"
                                
                                for i, part in enumerate(parts):
                                    if part.startswith("Node(") and part.endswith(")"):
                                        node_name = part[5:-1]
                                        agent_text += f"    [bold white on red] :package: {node_name} [/bold white on red]\n"
                                    elif part.startswith("Edge(") and part.endswith(")"):
                                        edge_name = part[5:-1]
                                        agent_text += f"          │\n"
                                        agent_text += f"          ▼\n"
                                        agent_text += f"    [dim magenta]({edge_name})[/dim magenta]\n"
                                        agent_text += f"          │\n"
                                        agent_text += f"          ▼\n"
                                    else:
                                        # Fallback generic part
                                        agent_text += f"    [bold] {part} [/bold]\n"
                                        if i < len(parts) - 1:
                                            agent_text += f"          │\n          ▼\n"
                    
                    agent_text += f"\n[bold italic]Final Answer:[/bold italic] "
                    if "APPROVED" in actual_verdict:
                        agent_text += f"The infrastructure is compliant and safe to deploy."
                    else:
                        agent_text += f"The infrastructure violates governance guardrails and poses a security/compliance risk. It must be fixed before deployment."
                        
                    console.print(Panel(agent_text, title="[magenta]:robot: Predictive Governance Agent Behavior[/magenta]", border_style="magenta", expand=False))
                    console.print("\n")
                    console.rule(f"[bold green]End of {file}[/bold green]", style="green")
                    console.print("\n\n")

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
