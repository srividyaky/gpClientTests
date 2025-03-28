import pytest
import uuid
import logging
from utils.ssh_utils import SSHConnection
from utils.helpers import setup_logging
from utils import config
from pytest_reportportal.rp_logging import RPLogger

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def rp_logger():
    """Fixture to provide Report Portal logger"""
    logger = RPLogger(__name__)
    return logger


@pytest.fixture(scope="session")
def ssh_connection(rp_logger):
    """Provide an SSH connection to the client VM"""
    connection = SSHConnection()
    rp_logger.info(f"Establishing SSH connection to client VM: {config.CLIENT_HOST}")

    if not connection.connect():
        rp_logger.error("Failed to establish SSH connection to client VM")
        pytest.fail("Failed to establish SSH connection to client VM")

    # Check Greenplum database status on target host
    rp_logger.info(f"Checking Greenplum status on target host: {config.HOST}")
    if not connection.check_greenplum_status():
        rp_logger.error("Greenplum database is not running on target host")
        pytest.fail("Greenplum database is not running")

    yield connection

    # Close connection at the end of the session
    rp_logger.info("Closing SSH connection")
    connection.close()

@pytest.fixture(scope="function")
def unique_name():
    """Generate a unique name for test objects"""
    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def test_database(ssh_connection, unique_name, rp_logger):
    """Create and drop a test database for each test"""
    db_name = f"db_{unique_name}"

    # Create database
    rp_logger.info(f"Creating test database: {db_name}")
    success, output, error = ssh_connection.execute_command(
        f"source ~/.bashrc && createdb -h {config.HOST} -U {config.USERNAME} {db_name}"
    )

    if not success:
        rp_logger.error(f"Failed to create test database: {error}")
        pytest.fail(f"Failed to create test database: {error}")

    yield db_name

    # Drop database after test
    rp_logger.info(f"Dropping test database: {db_name}")
    ssh_connection.execute_command(
        f"source ~/.bashrc && dropdb -h {config.HOST} -U {config.USERNAME} {db_name}"
    )
