import os
import schedule
import subprocess
import time
import logging
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

GOOGLE_CHAT_WEBHOOK_URL = 'https://chat.googleapis.com/v1/spaces/AAAA65Gz3uI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=MRMfBe9-1X9uExmc5Vn89imxxe1tn1fH3LPuF2H19iY'

BASE_DIRECTORY = os.getcwd() 
TESTCASES_DIRECTORY = os.path.join(BASE_DIRECTORY,'testcases')

logging.info(f"Base directory: {BASE_DIRECTORY}")
logging.info(f"Test cases directory: {TESTCASES_DIRECTORY}")

if not os.path.exists(TESTCASES_DIRECTORY):
    logging.error(f"The test cases directory does not exist: {TESTCASES_DIRECTORY}")
else:
    logging.info(f"Contents of test cases directory: {os.listdir(TESTCASES_DIRECTORY)}")

robot_files = [
    os.path.join(root, file)
    for root, _, files in os.walk(TESTCASES_DIRECTORY)
    for file in files if file.endswith(".robot")
]

if not robot_files:
    logging.error("No .robot files found in the specified test cases directory.")
else:
    logging.info(f"Found .robot files: {robot_files}")

def build():
    """Run all collected Robot Framework test files and send notifications."""
    for suite in robot_files:
        suite_name = os.path.splitext(os.path.basename(suite))[0]

        # Run the test without output reports
        command = f"robot --log NONE --report NONE --output NONE \"{suite}\""
        logging.info(f"Running command: {command}")

        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            status = "PASSED"
            output_message = result.stdout
            logging.info(f"Test suite '{suite_name}' passed successfully.")
        except subprocess.CalledProcessError as e:
            result = e
            status = "FAILED"
            output_message = result.stdout + result.stderr
            logging.error(f"Test suite '{suite_name}' failed. Error: {e.stderr}")

        send_notification(suite_name, output_message, status)

def send_notification(suite, message, status):
    """Send a notification to Google Chat with the test results."""
    lines = message.splitlines()
    summary = lines[0] if lines else "No summary available"
    detailed_log = "\n".join(lines[1:]).strip() if lines else "No detailed log available"

    payload = {
        'text': (
            f'*Test Suite:* {suite}\n'
            f'*Status:* **{status}**\n'
            f'*Summary:*\n```\n{summary}\n```\n'
            f'*Detailed Log:*\n```\n{detailed_log}\n```'
        ),
    }

    try:
        response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Notification sent successfully - Suite: {suite} Status: {status}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send notification: {e}")

if __name__ == "__main__":
    build()
