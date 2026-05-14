import os
import json
from datetime import datetime
from jinja2 import Environment, BaseLoader

# Jinja2 template for the HTML report
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IaC Governance Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --border: #334155;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }
        h1, h2, h3 { color: #fff; }
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border);
        }
        .summary {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-bottom: 3rem;
        }
        .stat-card {
            background: var(--surface-color);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            text-align: center;
            min-width: 150px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .stat-card.passed .value { color: var(--success); }
        .stat-card.failed .value { color: var(--danger); }
        .stat-card .value { font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem; }
        .stat-card .label { color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.875rem; }
        
        .test-case {
            background: var(--surface-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 6px solid var(--border);
        }
        .test-case.status-pass { border-left-color: var(--success); }
        .test-case.status-fail { border-left-color: var(--danger); }
        
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        .test-title { font-size: 1.25rem; font-weight: 600; margin: 0; word-break: break-all; }
        .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .badge.pass { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .badge.fail { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .badge.skipped { background: rgba(234, 179, 8, 0.2); color: #eab308; }
        
        .test-case.status-skipped { border-left-color: #eab308; opacity: 0.8; }
        
        .action-links {
            margin-top: 1rem;
            display: flex;
            gap: 1rem;
        }
        .action-links a {
            text-decoration: none;
            color: var(--accent);
            font-size: 0.875rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(59, 130, 246, 0.1);
            border-radius: 6px;
            transition: all 0.2s;
        }
        .action-links a:hover {
            background: rgba(59, 130, 246, 0.2);
            color: #fff;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        .meta-item .label { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 0.25rem; }
        .meta-item .value { font-weight: 500; }
        
        .output-block {
            background: #000;
            color: #fff;
            padding: 1rem;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            margin-top: 1rem;
            font-size: 0.875rem;
        }
        
        /* Mermaid styling for dark mode */
        .mermaid { background: transparent; padding: 1rem; border-radius: 8px; display: flex; justify-content: center; }

        /* Neuron Glow Effects */
        .mermaid .node rect { stroke-width: 2px; transition: all 0.3s; }
        .mermaid .node.active rect { stroke: #3b82f6 !important; fill: rgba(59, 130, 246, 0.2) !important; filter: drop-shadow(0 0 8px #3b82f6); }
        .mermaid .node.danger rect { stroke: #ef4444 !important; fill: rgba(239, 68, 68, 0.2) !important; filter: drop-shadow(0 0 12px #ef4444); }
        .mermaid .node.success rect { stroke: #10b981 !important; fill: rgba(16, 185, 129, 0.2) !important; filter: drop-shadow(0 0 8px #10b981); }
        
        .brain-map-container {
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            background: rgba(15, 23, 42, 0.5);
            position: relative;
            overflow: hidden;
        }
        .brain-map-container::after {
            content: "AGENT NEURAL MAP";
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 0.6rem;
            color: var(--text-muted);
            letter-spacing: 2px;
        }
    </style>
    <script>
        mermaid.initialize({ 
            startOnLoad: true, 
            theme: 'dark',
            flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
        });
    </script>
</head>
<body>
    <div class="header">
        <h1>IaC Governance Validation Report</h1>
        <p style="color: var(--text-muted)">Generated on {{ timestamp }}</p>
    </div>

    <div class="summary">
        <div class="stat-card">
            <div class="value">{{ total_tests }}</div>
            <div class="label">Total Tests</div>
        </div>
        <div class="stat-card passed">
            <div class="value">{{ passed_tests }}</div>
            <div class="label">Passed</div>
        </div>
        <div class="stat-card failed">
            <div class="value">{{ failed_tests }}</div>
            <div class="label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="value" style="color: #eab308;">{{ skipped_tests }}</div>
            <div class="label">Skipped</div>
        </div>
    </div>
    
    <div style="text-align: center; margin-bottom: 2rem;">
        <a href="docs/Sovereign_Infrastructure_Governance.pdf" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
            📚 View Official Architecture & Governance Documentation
        </a>
    </div>

    {% if global_graph_mermaid %}
    <div class="test-case" style="border-left-color: var(--accent);">
        <h3 class="test-title" style="margin-bottom: 1rem;">🌐 Global Security Graph Network (Agent Knowledge Base)</h3>
        <p style="color: var(--text-muted); margin-bottom: 1rem;">This is the topological network the Predictive Governance Agent consults to detect toxic combinations and blast radius.</p>
        <div class="mermaid">
            {{ global_graph_mermaid }}
        </div>
    </div>
    {% endif %}

    <div class="test-list">
        {% for test in tests %}
        {% set status_class = 'skipped' if test.skipped else ('pass' if test.passed else 'fail') %}
        <div class="test-case status-{{ status_class }}">
            <div class="test-header">
                <h3 class="test-title">{{ test.path }}</h3>
                <span class="badge {{ status_class }}">
                    {{ 'SKIPPED' if test.skipped else ('PASS' if test.passed else 'FAIL') }}
                </span>
            </div>
            
            <p><strong>Expected:</strong> {{ test.expected }} | <strong>Actual:</strong> {{ test.actual }}</p>
            
            {% if test.metadata %}
            <div class="metadata-grid">
                {% if test.metadata.name %}
                <div class="meta-item">
                    <div class="label">Scenario Name</div>
                    <div class="value">{{ test.metadata.name }}</div>
                </div>
                {% endif %}
                {% if test.metadata.certification %}
                <div class="meta-item">
                    <div class="label">Certification</div>
                    <div class="value">{{ test.metadata.certification }}</div>
                </div>
                {% endif %}
                {% if test.metadata.severity %}
                <div class="meta-item">
                    <div class="label">Severity</div>
                    <div class="value">{{ test.metadata.severity }}</div>
                </div>
                {% endif %}
            </div>
            {% if test.metadata.description %}
            <p>{{ test.metadata.description }}</p>
            {% endif %}
            
            <div class="brain-map-container">
                <h4>🧠 Sentinel Agent Neural Logic Map</h4>
                <div class="mermaid">
                    graph LR
                    Input[("HCL Plan")] --> L1["💰 Cost"]
                    L1 --> L2["🛡️ OPA"]
                    L2 --> L3["🔮 Firefly"]
                    
                    L3 --> Query{"Graph"}
                    Query -- "MATCH" --> SecurityGraph[("Security Graph")]
                    SecurityGraph -- "Match" --> Analysis["Predictive Analysis"]
                    Analysis --> Verdict{"Verdict"}
                    
                    classDef default fill:#1e293b,stroke:#334155,color:#f8fafc;
                    classDef active fill:#3b82f633,stroke:#3b82f6,stroke-width:2px;
                    classDef danger fill:#ef444433,stroke:#ef4444,stroke-width:3px;
                    classDef success fill:#10b98133,stroke:#10b981,stroke-width:2px;

                    class Input active;
                    {% if test.simulated %}
                        class L1,L2,L3 active;
                    {% endif %}
                    {% if test.skipped %}
                        class L1,L2,L3,Query,Verdict default;
                    {% else %}
                        class L1,L2,L3 active;
                        class Query active;
                        class SecurityGraph active;
                        {% if test.passed %}
                            class Analysis success;
                            class Verdict success;
                        {% else %}
                            class Analysis danger;
                            class Verdict danger;
                        {% endif %}
                    {% endif %}
                </div>
            </div>

            {% if test.metadata.attack_path %}
            <div class="diagram-section">
                <h4>📊 Predictive Graph Context: Toxic Combination Found</h4>
                <p style="color: var(--text-muted); font-size: 0.875rem;">Sub-graph isolated from schema/security_graph.json during neural activation:</p>
                <div class="mermaid">
                    graph LR
                    {% set logic = test.metadata.attack_path.logic %}
                    {% if logic %}
                        %% Convert Logic "Node(X) -> Edge(Y) -> Node(Z)" to Mermaid syntax
                        {% set logic = logic.replace('Node(', '').replace('Edge(', '|').replace(') ->', '| -->').replace(')', '') %}
                        {{ logic }}
                        classDef danger fill:#ef444433,stroke:#ef4444,stroke-width:3px;
                        class A,B,C,D,E,F,G,H,I,J danger;
                    {% else %}
                        A[Start] --> B[End]
                    {% endif %}
                </div>
            </div>
            {% endif %}
            {% endif %}
            
            <div class="action-links">
                <a href="{{ test.path }}" target="_blank">📄 View Source Code</a>
                {% if test.metadata and test.metadata.name %}
                <a href="docs/Sovereign_Infrastructure_Governance.pdf" target="_blank">📖 Read Docs about this Benchmark</a>
                {% endif %}
            </div>
            
            {% if test.output %}
            <h4>Validation Feedback</h4>
            <div class="output-block">{{ test.output }}</div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def generate_html_report(results, output_path="test_report.html"):
    passed = sum(1 for r in results if r.get('passed') and not r.get('skipped'))
    skipped = sum(1 for r in results if r.get('skipped'))
    failed = len(results) - passed - skipped
    
    # Simple logic converter to mermaid
    for r in results:
        if r.get('metadata') and r['metadata'].get('attack_path') and r['metadata']['attack_path'].get('logic'):
            # Basic parsing of our custom format: Node(Account1:EC2) -> Edge(kms:PutKeyPolicy) -> Node(Account2:KMS)
            # Desired Mermaid: A[Account1:EC2] -- kms:PutKeyPolicy --> B[Account2:KMS]
            logic_str = r['metadata']['attack_path']['logic']
            parts = logic_str.split('->')
            mermaid_lines = []
            
            # Simple conversion if it matches the standard 3-part format
            if len(parts) >= 3 and 'Node(' in parts[0] and 'Edge(' in parts[1] and 'Node(' in parts[2]:
                node1 = parts[0].strip().replace('Node(', '').replace(')', '')
                edge = parts[1].strip().replace('Edge(', '').replace(')', '')
                node2 = parts[2].strip().replace('Node(', '').replace(')', '')
                
                # Make safe IDs
                id1 = ''.join(e for e in node1 if e.isalnum())
                id2 = ''.join(e for e in node2 if e.isalnum())
                
                mermaid_lines.append(f'{id1}["{node1}"] -- "{edge}" --> {id2}["{node2}"]')
                r['metadata']['attack_path']['logic'] = "\\n".join(mermaid_lines)
            else:
                 # Fallback
                 r['metadata']['attack_path']['logic'] = 'A["Start"] --> B["End"]'

    
    template = Environment(loader=BaseLoader()).from_string(REPORT_TEMPLATE)
    
    # Generate global security graph mermaid
    global_graph_mermaid = ""
    try:
        import json
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
            global_graph_mermaid = "\n".join(lines)
    except Exception:
        pass

    html_content = template.render(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_tests=len(results),
        passed_tests=passed,
        failed_tests=failed,
        skipped_tests=skipped,
        tests=results,
        global_graph_mermaid=global_graph_mermaid
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path
