import os
import sys
from workflow.tools import GovernanceManagerTool

def test_all_examples():
    tool = GovernanceManagerTool()
    test_dirs = ["examples"]

    # Map of filename or path to expected verdict
    expectations = {
        "mandatory_tagging.tf": "DENIED",
        "high_cost_infrastructure.tf": "DENIED",
        "secure_database.tf": "DENIED",
        "pci_network_segmentation.tf": "DENIED",
        "developer_role_violation.tf": "DENIED",
        "standard_s3_bucket.tf": "APPROVED",
        "governed_infrastructure.tf": "DENIED",

        # Benchmarks - Account 1 (Source)
        "benchmarks/scenario-001-shadow-admin/account_1_setup.tf": "DENIED", # aws_iam_role
        "benchmarks/scenario-002-public-private-bridge/account_1_setup.tf": "DENIED", # aws_vpc/aws_subnet
        "benchmarks/scenario-003-artifact-poisoning/account_1_setup.tf": "DENIED", # aws_iam_role
        "benchmarks/scenario-004-kms-decryption/account_1_setup.tf": "APPROVED",

        # Benchmarks - Account 2 (Target)
        "benchmarks/scenario-001-shadow-admin/account_2_target.tf": "DENIED", # aws_iam_role
        "benchmarks/scenario-002-public-private-bridge/account_2_target.tf": "DENIED", # aws_vpc/aws_db_instance
        "benchmarks/scenario-003-artifact-poisoning/account_2_target.tf": "DENIED", # Firefly blocks unencrypted S3
        "benchmarks/scenario-004-kms-decryption/account_2_target.tf": "APPROVED",
    }

    results = []
    failed_tests = []

    print("\n" + "="*60)
    print("🔍 Testing all examples and benchmarks in " + ", ".join(test_dirs))
    print("="*60 + "\n")

    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
        for root, dirs, files in os.walk(test_dir):
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

                    # Check expectations using the full path if available, or just the filename
                    expected_verdict = expectations.get(path, expectations.get(file, "APPROVED"))

                    if actual_verdict == expected_verdict:
                        print(f"✅ {path}: {actual_verdict} (Expected {expected_verdict})")
                    else:
                        print(f"❌ {path}: {actual_verdict} (Expected {expected_verdict})")
                        print(f"Output:\n{verdict_output}")
                        failed_tests.append(path)

    print("\n" + "="*60)
    if not failed_tests:
        print("✅ All examples and benchmarks behaved as expected!")
        print("="*60)
    else:
        print(f"❌ Some tests failed to meet expectations: {', '.join(failed_tests)}")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    test_all_examples()
