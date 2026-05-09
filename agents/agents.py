from crewai import Agent
from workflow.tools import NetworkInventoryTool, CloudCostEstimatorTool, OPAVerifierTool

class GovernanceAgents:
    def architect_agent(self):
        return Agent(
            role='Cloud Infrastructure Architect',
            goal='Generate secure, cost-effective, and compliant Terraform (HCL) code.',
            backstory="""You are a senior Cloud Architect.
            You ALWAYS:
            1. Use the 'governor' custom provider for VPC, Subnet, IAM Roles, and Security Groups to ensure Infrastructure Sovereignty.
            2. Use the 'standard-application' Golden Path module whenever possible.
            3. Include mandatory tags: CostCenter and Project.
            4. Ensure RDS and S3 are encrypted and private.
            5. Use the NetworkInventoryTool only when the custom provider is not applicable.""",
            tools=[NetworkInventoryTool()],
            verbose=True,
            allow_delegation=False
        )

    def auditor_agent(self):
        return Agent(
            role='Security and FinOps Auditor',
            goal='Audit HCL code using OPA policies and Cost Estimation tools.',
            backstory="""You are a strict compliance officer.
            You use the CloudCostEstimatorTool to check for budget violations ($100 limit).
            You use the OPAVerifierTool to validate the final plan against technical guardrails (PCI, IAM, Networking).
            You provide detailed feedback to the Architect if a plan is DENIED.""",
            tools=[CloudCostEstimatorTool(), OPAVerifierTool()],
            verbose=True,
            allow_delegation=True
        )

    def sentinel_agent(self):
        return Agent(
            role='Cloud Sentinel',
            goal='Detect drifts and toxic combinations in the environment.',
            backstory="""You monitor the 'actual_state.json' and the Security Graph.
            You identify when the real world deviates from the HCL definition (Drift)
            and alert the Architect for remediation.""",
            verbose=True,
            allow_delegation=False
        )
