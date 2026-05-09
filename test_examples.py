import os
import sys
from workflow.tools import GovernanceManagerTool

def test_all_examples():
    tool = GovernanceManagerTool()
    examples_dir = "examples"

    # Map of filename to expected verdict
    # If not in map, we assume it should be APPROVED (unlikely for many examples)
    expectations = {
        "mandatory_tagging.tf": "DENIED",
        "high_cost_infrastructure.tf": "DENIED",
        "secure_database.tf": "DENIED", # Likely missing tags or something else
        "pci_network_segmentation.tf": "DENIED",
        "developer_role_violation.tf": "DENIED",
        "standard_s3_bucket.tf": "APPROVED",
        "governed_infrastructure.tf": "DENIED", # Contains a vulnerable aws_vpc
    }

    results = []
    failed_tests = []

    print("\n" + "="*60)
    print("🔍 Testing all examples in " + examples_dir)
    print("="*60 + "\n")

    for root, dirs, files in os.walk(examples_dir):
        for file in files:
            if file.endswith(".tf"):
                path = os.path.join(root, file)
                print(f"Testing {path}...")

                with open(path, "r") as f:
                    hcl_content = f.read()

                verdict_output = tool._run(hcl_content)

                # Determine actual verdict
                if "VERDICT: APPROVED" in verdict_output:
                    actual_verdict = "APPROVED"
                elif "VERDICT: DENIED" in verdict_output:
                    actual_verdict = "DENIED"
                elif "VERDICT: CRITICAL FAILURE" in verdict_output:
                    actual_verdict = "DENIED" # Treat critical failure as a form of denial for now
                else:
                    actual_verdict = "ERROR"

                expected_verdict = expectations.get(file, "APPROVED")

                if actual_verdict == expected_verdict:
                    print(f"✅ {file}: {actual_verdict} (Expected {expected_verdict})")
                else:
                    print(f"❌ {file}: {actual_verdict} (Expected {expected_verdict})")
                    print(f"Output:\n{verdict_output}")
                    failed_tests.append(file)

    print("\n" + "="*60)
    if not failed_tests:
        print("✅ All examples behaved as expected!")
        print("="*60)
    else:
        print(f"❌ Some examples failed to meet expectations: {', '.join(failed_tests)}")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    test_all_examples()
