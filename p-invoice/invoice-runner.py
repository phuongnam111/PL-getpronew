import logging
import requests
import shutil
import sys
from subprocess import run, CalledProcessError, TimeoutExpired
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import time
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

# Configuration
CONFIG = {
    "GOOGLE_CHAT_WEBHOOK_URL": os.getenv("GOOGLE_CHAT_WEBHOOK_URL"),
    "GITLAB_BASE_URL": os.getenv("GITLAB_BASE_URL"),
    "DIRECTORIES_TO_SCAN": ["invoice-fe","invoice-be"],
    "PYCACHE": "__pycache__",
    "PYTHON_EXTENSION": ".py",
    "SUCCESS_EMOJI": "💚",
    "FAIL_EMOJI": "🍎",
    "TIMEOUT_SECONDS": 300,  # 5 minutes
    "MAX_LOG_LINES": 3,
    "MAX_WORKERS": 4,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 2,
    "NOTIFICATION_DELAY": 2,  # Delay between consecutive notifications (seconds)
}
# Debug environment variable loading
logging.debug(f"Loaded GOOGLE_CHAT_WEBHOOK_URL: {CONFIG['GOOGLE_CHAT_WEBHOOK_URL']}")
logging.debug(f"Loaded GITLAB_BASE_URL: {CONFIG['GITLAB_BASE_URL']}")

# Skip notification if GOOGLE_CHAT_WEBHOOK_URL is not set
NOTIFICATIONS_ENABLED = bool(CONFIG["GOOGLE_CHAT_WEBHOOK_URL"])
if not NOTIFICATIONS_ENABLED:
    logging.warning("GOOGLE_CHAT_WEBHOOK_URL is not set. Notifications will be skipped.")

# Warn if GITLAB_BASE_URL is not set
if not CONFIG["GITLAB_BASE_URL"]:
    logging.warning("GITLAB_BASE_URL is not set. GitLab links will be omitted.")

@dataclass
class TestResult:
    file_path: Path
    status: str
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None

def collect_test_files(directories: List[str]) -> List[Path]:
    """Collects Python test files, excluding __pycache__."""
    test_files = []
    script_path = Path(__file__)
    
    for directory in directories:
        dir_path = script_path.parent / directory
        if not dir_path.exists():
            logging.warning(f"Directory does not exist: {dir_path}")
            continue

        for file_path in dir_path.rglob(f"*{CONFIG['PYTHON_EXTENSION']}"):
            if (
                file_path.name != script_path.name
                and CONFIG["PYCACHE"] not in file_path.parts
                and file_path.name != "config.py"
                and file_path.name != "__init__.py"
            ):
                test_files.append(file_path)
    return test_files

def clear_pycache() -> None:
    """Safely clears __pycache__ directories."""
    for pycache_path in Path.cwd().rglob(CONFIG["PYCACHE"]):
        if pycache_path.is_dir() and pycache_path.name == CONFIG["PYCACHE"]:
            try:
                shutil.rmtree(pycache_path)
                logging.info(f"Deleted: {pycache_path}")
            except OSError as e:
                logging.error(f"Failed to delete {pycache_path}: {e}")

def send_notification(test_result: TestResult, max_retries: int = CONFIG["RETRY_ATTEMPTS"]) -> bool:
    """Sends a professional test report with retry mechanism, rate limiting, and exponential backoff."""
    # Add delay to prevent hitting rate limits
    time.sleep(CONFIG["NOTIFICATION_DELAY"])

    log_lines = test_result.output.splitlines()
    error_lines = [line for line in log_lines if any(kw in line for kw in ["ERROR", "FAIL", "Traceback"])]
    summary_logs = "\n".join(log_lines[-CONFIG["MAX_LOG_LINES"]:]) if log_lines else "No output"
    exec_time = f"{test_result.execution_time:.2f}s" if test_result.execution_time else "N/A"

    message = {
        "cardsV2": {
            "cardId": f"Kfinance-Report{test_result.file_path.stem}",
            "card": {
                "header": {
                    "title": f"{CONFIG['FAIL_EMOJI'] if test_result.status == 'FAILED' else CONFIG['SUCCESS_EMOJI']} Test Report",
                    "subtitle": test_result.file_path.name,
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "decoratedText": {
                                    "topLabel": "TEST STATUS",
                                    "text": test_result.status,
                                    "startIcon": {"knownIcon": "CHECK" if test_result.status == "COMPLETED" else "CLEAR"},
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "ERRORS",
                                    "text": str(len(error_lines)),
                                    "startIcon": {"knownIcon": "BUG"},
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "DURATION",
                                    "text": exec_time,
                                    "startIcon": {"knownIcon": "CLOCK"},
                                }
                            },
                        ]
                    },
                    *([{
                        "header": "🛑 Critical Errors",
                        "collapsible": True,
                        "widgets": [{"textParagraph": {"text": f"```\n{error_lines[0] if error_lines else 'No errors'}\n```"}}],
                    }] if error_lines else []),
                    {
                        "header": "📝 Execution Summary",
                        "collapsible": False,
                        "widgets": [{"textParagraph": {"text": f"```\n{summary_logs}\n```"}}],
                    },
                    {
                        "header": "📜 Full Execution Logs",
                        "collapsible": True,
                        "widgets": [{"textParagraph": {"text": f"```\n{test_result.output or 'No logs available'}\n```"}}],
                    },
                    {
                        "widgets": [
                            {
                                "buttonList": {
                                    "buttons": [
                                        {
                                            "text": "View in GitLab",
                                            "onClick": {
                                                "openLink": {
                                                    "url": f"{CONFIG['GITLAB_BASE_URL']}/-/pipeline_schedules/?id={test_result.file_path.stem}"
                                                }
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                ],
            },
        }
    }

    for attempt in range(max_retries):
        try:
            with requests.Session() as session:
                response = session.post(
                    CONFIG["GOOGLE_CHAT_WEBHOOK_URL"],
                    json=message,
                    timeout=10,
                )
                response.raise_for_status()
                return True
        except requests.RequestException as e:
            logging.warning(f"Notification attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds
                delay = CONFIG["RETRY_DELAY"] * (2 ** attempt)
                logging.info(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
    logging.error(f"Failed to send notification for {test_result.file_path.name} after {max_retries} attempts")
    return False

def analyze_output(output: str) -> str:
    """Analyzes output log for errors."""
    error_indicators = ["ERROR", "FAIL", "Timeout", "Traceback", "Exception"]
    return "FAILED" if any(indicator in output for indicator in error_indicators) else "COMPLETED"

def run_test_script(file_path: Path) -> TestResult:
    """Runs a test script with proper error handling."""
    logging.info(f"Running: {file_path}")
    start_time = time.time()
    python_cmd = sys.executable

    try:
        result = run(
            [python_cmd, str(file_path)],
            capture_output=True,
            text=True,
            timeout=CONFIG["TIMEOUT_SECONDS"],
            check=True,
        )
        output = result.stdout + result.stderr
        status = analyze_output(output)
        return TestResult(
            file_path=file_path,
            status=status,
            output=output,
            execution_time=time.time() - start_time,
        )
    except TimeoutExpired as e:
        error_msg = f"Timeout after {CONFIG['TIMEOUT_SECONDS']}s"
        logging.error(f"{file_path}: {error_msg}")
        return TestResult(
            file_path=file_path,
            status="FAILED",
            output=str(e),
            error=error_msg,
            execution_time=time.time() - start_time,
        )
    except CalledProcessError as e:
        error_msg = f"Failed with code {e.returncode}"
        logging.error(f"{file_path}: {error_msg}")
        return TestResult(
            file_path=file_path,
            status="FAILED",
            output=e.stdout + e.stderr,
            error=error_msg,
            execution_time=time.time() - start_time,
        )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(f"{file_path}: {error_msg}")
        return TestResult(
            file_path=file_path,
            status="FAILED",
            output="",
            error=error_msg,
            execution_time=time.time() - start_time,
        )

def run_tests() -> List[TestResult]:
    """Runs all tests in parallel."""
    test_files = collect_test_files(CONFIG["DIRECTORIES_TO_SCAN"])
    if not test_files:
        logging.info("No test files found")
        return []

    with ThreadPoolExecutor(max_workers=CONFIG["MAX_WORKERS"]) as executor:
        return list(executor.map(run_test_script, test_files))

def main() -> None:
    """Main execution function with modular design."""
    try:
        test_results = run_tests()
        failed_count = sum(1 for result in test_results if result.status == "FAILED")

        for result in test_results:
            send_notification(result)

        clear_pycache()

        if failed_count > 0:
            logging.error(f"{failed_count}/{len(test_results)} tests failed!")
            sys.exit(1)

        logging.info("All tests passed successfully")
    except Exception as e:
        logging.critical(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()