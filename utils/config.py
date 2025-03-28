import os
import json
import platform
import codecs
import logging

def get_current_platform():
    """Detect current platform - can be extended with more detailed detection"""
    system = platform.system().lower()
    if system == "linux":
        # Check for Rocky Linux and version
        try:
            with open("/etc/os-release", "r") as f:
                os_info = f.read()
                if "rocky" in os_info.lower():
                    if "VERSION_ID=\"8" in os_info:
                        return "rocky8"
                    elif "VERSION_ID=\"9" in os_info:
                        return "rocky9"
            # Add more Linux distro detection as needed
        except FileNotFoundError:
            pass
    return system  # fallback to just 'linux', 'windows', etc.

# Determine base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Load platform configurations from the JSON file
CONFIG_FILE = os.environ.get("GPDB_CONFIG_FILE",
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform_config.json"))

# Determine current platform with explicit environment variable handling
CURRENT_PLATFORM = os.environ.get("GPDB_PLATFORM", get_current_platform())
GREENPLUM_CLIENTS_PATH = os.environ.get(
    "GREENPLUM_CLIENTS_PATH",
    "/usr/local/greenplum-db-clients-7.4.0/greenplum_clients_path.sh"
)

try:
    with codecs.open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
        PLATFORM_CONFIGS = json.load(f)
except Exception as e:
    logger.warning(f"Failed to load config file: {e}")
    PLATFORM_CONFIGS = {}

# Select platform configuration
platform_config = PLATFORM_CONFIGS.get(CURRENT_PLATFORM, PLATFORM_CONFIGS.get("default", {}))

# Log detailed configuration
logger.info("--- Detailed Configuration ---")
logger.info(f"GPDB_PLATFORM env var: {os.environ.get('GPDB_PLATFORM', 'Not set')}")
logger.info(f"Detected platform: {CURRENT_PLATFORM}")
logger.info(f"Selected Host: {platform_config.get('client_host')}")
logger.info("----------------------------")

# Configuration values for Client (source) VM
CLIENT_HOST = os.environ.get("GPDB_CLIENT_HOST", platform_config.get("client_host"))
CLIENT_USERNAME = os.environ.get("GPDB_CLIENT_USERNAME", platform_config.get("client_username"))
CLIENT_PASSWORD = os.environ.get("GPDB_CLIENT_PASSWORD", platform_config.get("client_password"))

# Configuration values for Greenplum (target) Database
HOST = os.environ.get("GPDB_HOST", platform_config.get("greenplum_host"))
USERNAME = os.environ.get("GPDB_USERNAME", platform_config.get("greenplum_username"))
PASSWORD = os.environ.get("GPDB_PASSWORD", platform_config.get("greenplum_password"))
PORT = int(os.environ.get("GPDB_PORT", platform_config.get("port", 5432)))
DATABASE = os.environ.get("GPDB_DATABASE", platform_config.get("database", "postgres"))

# Test Data Directory
TEST_DATA_DIR = os.path.join(BASE_DIR, "test_data")
os.makedirs(TEST_DATA_DIR, exist_ok=True)