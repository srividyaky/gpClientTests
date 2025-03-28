import logging
from utils import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestCreateDropDb:
    """Tests for Greenplum client tools"""

    def test_createdb_dropdb(self, ssh_connection, unique_name, rp_logger):
        """Test createdb and dropdb functionality"""
        # Test variables
        db_name = f"test_db_{unique_name}"

        # Test createdb
        rp_logger.info(f"Testing createdb with database: {db_name}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && createdb -h {config.HOST} -U {config.USERNAME} {db_name}"
        )
        rp_logger.debug(f"Command output: {output}")
        rp_logger.debug(f"Command error: {error}")
        assert success, f"Failed to create database: {error}"

        # Verify database exists
        rp_logger.info(f"Verifying database {db_name} exists")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -l | grep {db_name}"
        )
        assert success and db_name in output, f"Database {db_name} not found after creation"
        rp_logger.info(f"Database {db_name} successfully created")

        # Test dropdb
        rp_logger.info(f"Testing dropdb with database: {db_name}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && dropdb -h {config.HOST} -U {config.USERNAME} {db_name}"
        )
        rp_logger.debug(f"Command output: {output}")
        rp_logger.debug(f"Command error: {error}")
        assert success, f"Failed to drop database: {error}"

        # Verify database no longer exists
        rp_logger.info(f"Verifying database {db_name} no longer exists")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -l | grep {db_name}"
        )
        assert db_name not in output, f"Database {db_name} still exists after drop"
        rp_logger.info(f"Database {db_name} successfully dropped")
