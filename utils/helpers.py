import logging
import os
import subprocess
import csv
from . import config

logger = logging.getLogger(__name__)


def setup_logging():
    """Set up logging configuration"""
    # Ensure log directory exists
    log_dir = os.path.dirname(config.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    # Create log file if it doesn't exist
    if not os.path.exists(config.LOG_FILE):
        open(config.LOG_FILE, 'a').close()

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def run_local_command(command, env=None):
    """Run a command locally"""
    logger.debug(f"Running local command: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    stdout, stderr = process.communicate()
    exit_code = process.returncode

    output = stdout.decode('utf-8') if stdout else ""
    error = stderr.decode('utf-8') if stderr else ""

    if exit_code != 0:
        logger.warning(f"Command failed with exit code {exit_code}: {error}")

    return exit_code == 0, output, error


