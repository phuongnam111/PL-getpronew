import logging
import requests
import shutil
import sys
from subprocess import run, CalledProcessError, TimeoutExpired
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import time
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import platform
from dotenv import load_dotenv
import html

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
    "DIRECTORIES_TO_SCAN": ["payment-be","payment-be","payment-notify"],
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
    # Group errors: Traceback first, then other ERROR/FAIL lines
    traceback_lines = [line for line in log_lines if "Traceback" in line]
    other_error_lines = [line for line in log_lines if ("ERROR" in line or "FAIL" in line) and "WARNING" not in line]
    error_lines = traceback_lines + [l for l in other_error_lines if l not in traceback_lines]
    summary_logs = "\n".join(log_lines[-CONFIG["MAX_LOG_LINES"]:]) if log_lines else "No output"
    exec_time = f"{test_result.execution_time:.2f}s" if test_result.execution_time else "N/A"
    # utc + 7
    local_tz = timezone(timedelta(hours=7))
    now_local = datetime.now(local_tz)
    started_at = (now_local - timedelta(seconds=test_result.execution_time)).strftime("%Y-%m-%d %H:%M:%S %Z%z") if test_result.execution_time else "N/A"
    finished_at = now_local.strftime("%Y-%m-%d %H:%M:%S %Z%z")

    def to_monospace_html(text: str) -> str:
        safe = html.escape(text)
        safe = safe.replace("\n", "<br>")
        return f"<font face=\"monospace\">{safe}</font>"

    # Context info
    env_name = (
        os.getenv("ENV_NAME")
        or os.getenv("ENV")
        or os.getenv("CI_ENVIRONMENT_NAME")
        or os.getenv("APP_ENV")
        or os.getenv("PYTHON_ENV")
        or "gitlab"
    )
    git_branch = os.getenv("GIT_BRANCH") or os.getenv("BRANCH_NAME")
    host_name = os.getenv("HOSTNAME") or platform.node()
    context_bits = [f"env: {env_name}"]
    if git_branch:
        context_bits.append(f"branch: {git_branch}")
    if host_name:
        context_bits.append(f"host: {host_name}")
    context_line = " • ".join(context_bits)

    # Short path (relative to script directory)
    try:
        short_path = str(test_result.file_path.relative_to(Path(__file__).parent))
    except Exception:
        short_path = str(test_result.file_path.name)

    # Sanitize cardId to avoid invalid characters
    safe_card_id = "".join(c for c in test_result.file_path.stem if c.isalnum() or c in "_-")
    
    # Truncate long text to avoid API limits
    def truncate_text(text, max_length=1000):
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    # Create a simpler, more reliable, and better-formatted message card
    message = {
        "cardsV2": {
            "cardId": f"test-report-{safe_card_id}",
            "card": {
                "header": {
                    "title": f"{CONFIG['FAIL_EMOJI'] if test_result.status == 'FAILED' else CONFIG['SUCCESS_EMOJI']} Test Report • {test_result.file_path.name}",
                    "subtitle": f"{context_line}",
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "decoratedText": {
                                    "topLabel": "TEST STATUS",
                                    "text": test_result.status,
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "FILE",
                                    "text": to_monospace_html(short_path),
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "ERRORS",
                                    "text": str(len(error_lines)),
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "DURATION",
                                    "text": exec_time,
                                }
                            },
                            { "divider": {} },
                            {
                                "decoratedText": {
                                    "topLabel": "STARTED",
                                    "text": started_at,
                                }
                            },
                            {
                                "decoratedText": {
                                    "topLabel": "FINISHED",
                                    "text": finished_at,
                                }
                            },
                        ]
                    },
                    {
                        "header": "📝 Output (last lines)",
                        "collapsible": True,
                        "widgets": [{"textParagraph": {"text": truncate_text(to_monospace_html(summary_logs))}}],
                    },
                ],
            },
        }
    }

    # Add error section only if there are errors
    if error_lines:
        max_preview = 5
        preview = error_lines[:max_preview]
        remaining = len(error_lines) - len(preview)
        if remaining > 0:
            preview.append(f"(+{remaining} more lines truncated)")
        message["cardsV2"]["card"]["sections"].append({
            "header": "🛑 Critical Errors",
            "collapsible": True,
            "widgets": [{"textParagraph": {"text": truncate_text(to_monospace_html('\n'.join(preview)))}}],
        })

    # Add GitLab button only if URL is configured
    if CONFIG["GITLAB_BASE_URL"]:
        message["cardsV2"]["card"]["sections"].append({
            "widgets": [
                {
                    "buttonList": {
                        "buttons": [
                            {
                                "text": "View in GitLab",
                                "onClick": {
                                    "openLink": {
                                        "url": f"{CONFIG['GITLAB_BASE_URL']}/-/pipeline_schedules/?id={safe_card_id}"
                                    }
                                },
                            }
                        ]
                    }
                }
            ]
        })

    # Create a simple fallback message if the complex one fails
    fallback_message = {
        "text": f"{CONFIG['FAIL_EMOJI'] if test_result.status == 'FAILED' else CONFIG['SUCCESS_EMOJI']} **{test_result.file_path.name}**\n"
                f"Status: {test_result.status}\n"
                f"Duration: {exec_time}\n"
                f"Errors: {len(error_lines)}"
    }

    for attempt in range(max_retries):
        try:
            with requests.Session() as session:
                # Try complex message first
                response = session.post(
                    CONFIG["GOOGLE_CHAT_WEBHOOK_URL"],
                    json=message,
                    timeout=10,
                )
                response.raise_for_status()
                logging.info(f"Notification sent successfully for {test_result.file_path.name}")
                return True
        except requests.RequestException as e:
            logging.warning(f"Complex notification attempt {attempt + 1} failed: {e}")
            # Log response details for debugging
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logging.warning(f"API Error details: {error_detail}")
                except:
                    logging.warning(f"API Error response: {e.response.text}")
            
            # Try fallback simple message on last attempt
            if attempt == max_retries - 1:
                try:
                    logging.info(f"Trying fallback simple message for {test_result.file_path.name}")
                    with requests.Session() as session:
                        response = session.post(
                            CONFIG["GOOGLE_CHAT_WEBHOOK_URL"],
                            json=fallback_message,
                            timeout=10,
                        )
                        response.raise_for_status()
                        logging.info(f"Fallback notification sent successfully for {test_result.file_path.name}")
                        return True
                except requests.RequestException as fallback_e:
                    logging.error(f"Fallback notification also failed: {fallback_e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds
                delay = CONFIG["RETRY_DELAY"] * (2 ** attempt)
                logging.info(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
    
    logging.error(f"Failed to send notification for {test_result.file_path.name} after {max_retries} attempts")
    return False

def analyze_output(output: str) -> str:
    """Analyzes output log for errors."""
    # payment result verification - this is the primary success indicator
    if "Payment verify successful." in output:
        return "COMPLETED"
    
    critical_error_indicators = ["Traceback", "Exception", "Timeout"]
    if any(indicator in output for indicator in critical_error_indicators):
        return "FAILED"
    
    # Check for ERROR level logs, but exclude WARNING messages
    lines = output.splitlines()
    for line in lines:
        if "ERROR" in line and "WARNING" not in line:
            return "FAILED"
    
    # If we reach here, assume it's completed (no critical errors found)
    return "COMPLETED"

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