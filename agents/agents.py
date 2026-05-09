from crewai import Agent

class GovernanceAgents:
    def architect_agent(self):
        return Agent(
            role='Cloud Infrastructure Architect',
            goal='Generate secure and compliant Terraform (HCL) code based on user intent.',
            backstory="""You are a senior Cloud Architect with expertise in Terraform and AWS.
            You always use "Golden Path" modules and follow security best practices.
            You are proactive in adding mandatory tags like CostCenter and Project.""",
            verbose=True,
            allow_delegation=False
        )

    def auditor_agent(self):
        return Agent(
            role='Security Compliance Auditor',
            goal='Audit generated Terraform code against OPA policies and security graphs.',
            backstory="""You are a security expert. You analyze the output of OPA (Open Policy Agent)
            and Security Graphs to identify risks. You provide clear feedback on how to fix
            security violations or toxic combinations.""",
            verbose=True,
            allow_delegation=True
        )

    def sentinel_agent(self):
        return Agent(
            role='Cloud Sentinel (Context Analyst)',
            goal='Provide context from the current cloud environment and security graph.',
            backstory="""You have access to the Security Graph and existing cloud inventory.
            You help the Auditor identify "Toxic Combinations" that single policy checks might miss.""",
            verbose=True,
            allow_delegation=False
        )
