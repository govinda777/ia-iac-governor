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
            description=f"""Audit the following HCL code:
            {hcl_context}

            Steps:
            1. Estimate cost using CloudCostEstimatorTool.
            2. Convert HCL intent to a mock Plan JSON (simulated).
            3. Run OPAVerifierTool with the Plan JSON and Cost.
            4. If DENIED, explain precisely why.""",
            expected_output="An audit report (APPROVED or DENIED) with recommendations.",
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
