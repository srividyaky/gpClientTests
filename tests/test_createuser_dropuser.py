import logging
from utils import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestCreateDropUser:
    """Tests for Greenplum client tools"""

    def test_createuser_dropuser(self, ssh_connection, unique_name, rp_logger):
        """Test createuser and dropuser functionality"""
        # Test variables
        username = f"test_user_{unique_name}"
        password = "Test123!"

        # Test createuser - using expect-like approach for interactive password prompt
        rp_logger.info(f"Testing createuser with username: {username}")

        command = f"source ~/.bashrc && PGPASSWORD='{config.PASSWORD}' createuser -h {config.HOST} -U {config.USERNAME} -P -e {username} <<EOF\n{password}\n{password}\nEOF"

        success, output, error = ssh_connection.execute_command(command)
        rp_logger.debug(f"Createuser output: {output}")
        rp_logger.debug(f"Createuser error: {error}")
        assert success, f"Failed to create user: {error}"

        # Verify user exists
        rp_logger.info(f"Verifying user {username} exists")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -t -c \"SELECT 1 FROM pg_roles WHERE rolname='{username}'\""
        )
        assert success and "1" in output, f"User {username} not found after creation"
        rp_logger.info(f"User {username} successfully created")

        # Test dropuser
        rp_logger.info(f"Testing dropuser with username: {username}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && dropuser -h {config.HOST} -U {config.USERNAME} {username}"
        )
        rp_logger.debug(f"Dropuser output: {output}")
        rp_logger.debug(f"Dropuser error: {error}")
        assert success, f"Failed to drop user: {error}"

        # Verify user no longer exists
        rp_logger.info(f"Verifying user {username} no longer exists")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -t -c \"SELECT 1 FROM pg_roles WHERE rolname='{username}'\""
        )
        assert "1" not in output, f"User {username} still exists after drop"
        rp_logger.info(f"User {username} successfully dropped")