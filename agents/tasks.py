from crewai import Task

class GovernanceTasks:
    def generation_task(self, agent, user_intent):
        return Task(
            description=f"""Generate Terraform HCL code for the following intent: {user_intent}.
            Ensure you use proper tags (CostCenter, Project) and security defaults (encryption, private access).""",
            expected_output="A valid Terraform HCL code block.",
            agent=agent
        )

    def audit_task(self, agent, generated_code, security_graph_context):
        return Task(
            description=f"""Review the following Terraform code:
            {generated_code}

            Also, consider the Security Graph context:
            {security_graph_context}

            Validate if there are any OPA policy violations or toxic combinations.
            If violations exist, specify exactly what needs to be changed.""",
            expected_output="An audit report with 'APPROVED' or 'DENIED' status and detailed recommendations.",
            agent=agent
        )

    def remediation_task(self, agent, audit_report, original_code):
        return Task(
            description=f"""Based on the audit report:
            {audit_report}

            Correct the original Terraform code:
            {original_code}

            Ensure all security violations are fixed while maintaining the original intent.""",
            expected_output="The corrected Terraform HCL code.",
            agent=agent
        )
