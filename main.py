import os
import json
from agents.agents import GovernanceAgents
from agents.tasks import GovernanceTasks
from crewai import Crew, Process

def run_governance_poc(user_intent, use_mock=True):
    print(f"\n--- Iniciando PoC de Governança AI-Native ---")
    print(f"Intenção do Usuário: {user_intent}\n")

    # Load Security Graph Context
    with open('schema/security_graph.json', 'r') as f:
        security_context = json.load(f)

    agents = GovernanceAgents()
    tasks = GovernanceTasks()

    architect = agents.architect_agent()
    auditor = agents.auditor_agent()
    sentinel = agents.sentinel_agent()

    if use_mock:
        print("[INFO] Executando em modo de SIMULAÇÃO (Mock).")
        import simulate_poc
        simulate_poc.simulate()
    else:
        print("[INFO] Executando com Agentes CrewAI reais.")
        # Define tasks with proper dependencies
        gen_task = tasks.generation_task(architect, user_intent)

        audit_task = tasks.audit_task(auditor, "Result from Architecture generation", security_context)
        audit_task.context = [gen_task]

        remedy_task = tasks.remediation_task(architect, "Audit report feedback", "Original generated HCL")
        remedy_task.context = [gen_task, audit_task]

        # Real CrewAI execution (requires API Key)
        crew = Crew(
            agents=[architect, sentinel, auditor],
            tasks=[gen_task, audit_task, remedy_task],
            process=Process.sequential
        )

        result = crew.kickoff()
        print(f"\n--- Resultado Final ---\n{result}")

if __name__ == "__main__":
    intent = "Preciso de um bucket S3 para armazenar logs de auditoria do projeto Alpha."
    # Change use_mock to False if you have set your OPENAI_API_KEY
    run_governance_poc(intent, use_mock=True)
