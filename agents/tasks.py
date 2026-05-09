from crewai import Task

class GovernanceTasks:
    def generation_task(self, agent, user_intent):
        return Task(
            description=f"""Create Terraform HCL for: {user_intent}.
            Steps:
            1. Prioritize using the 'governor' provider resources (governor_vpc, governor_iam_role, governor_security_group).
            2. Use the 'standard-application' module for standard app deployments.
            3. Follow security best practices (encryption, private).
            4. Apply mandatory tags (CostCenter, Project).""",
            expected_output="A complete and valid Terraform HCL code block.",
            agent=agent
        )

    def audit_task(self, agent, hcl_context):
        return Task(
            description=f"""Audit the following HCL code using GovernanceManagerTool:
            {hcl_context}

            Steps:
            1. Pass the HCL code to GovernanceManagerTool.
            2. Analyze the report.
            3. If DENIED or CRITICAL FAILURE, explain precisely why and list all findings.
            4. Be sure to include any 'SUGGESTED FIX' in your report so the Architect can use it.""",
            expected_output="An audit report (APPROVED, DENIED or CRITICAL FAILURE) with recommendations and patches.",
            agent=agent
        )

    def remediation_task(self, agent, drift_context, original_hcl):
        return Task(
            description=f"""A drift was detected:
            {drift_context}

            Original HCL:
            {original_hcl}

            Generate the corrective Terraform HCL to restore the desired state and fix security gaps.""",
            expected_output="Corrective Terraform HCL code.",
            agent=agent
        )
