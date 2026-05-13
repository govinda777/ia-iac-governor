import time
import subprocess
import os

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout

def validate_sqs():
    print("Starting SQS latency tests against Floci at http://localhost:4566...")

    # Measure creation latency
    start_time = time.time()
    queue_url_output = run_cmd(["aws", "sqs", "create-queue", "--queue-name", "test-queue", "--endpoint-url=http://localhost:4566", "--output", "text", "--query", "QueueUrl"])
    queue_url = queue_url_output.strip()
    create_latency = (time.time() - start_time) * 1000
    print(f"Queue creation latency: {create_latency:.2f} ms")

    # Measure send message latency
    start_time = time.time()
    run_cmd(["aws", "sqs", "send-message", "--queue-url", queue_url, "--message-body", "Hello Floci", "--endpoint-url=http://localhost:4566"])
    send_latency = (time.time() - start_time) * 1000
    print(f"Send message latency: {send_latency:.2f} ms")

    # Measure receive message latency
    start_time = time.time()
    run_cmd(["aws", "sqs", "receive-message", "--queue-url", queue_url, "--endpoint-url=http://localhost:4566"])
    receive_latency = (time.time() - start_time) * 1000
    print(f"Receive message latency: {receive_latency:.2f} ms")

    # Clean up
    run_cmd(["aws", "sqs", "delete-queue", "--queue-url", queue_url, "--endpoint-url=http://localhost:4566"])

    print("All SQS benchmark tests passed successfully!")

if __name__ == "__main__":
    validate_sqs()
