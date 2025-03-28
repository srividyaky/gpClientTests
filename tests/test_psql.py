import logging
from utils import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestPsql:
    """Tests for core Greenplum client tools"""

    def test_psql_basic_query(self, ssh_connection, rp_logger):
        """Test basic psql query functionality"""
        # Test running a simple query
        rp_logger.info("Testing psql with a basic query")
        query = "SELECT version();"
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -c \"{query}\""
        )

        rp_logger.debug(f"Query output: {output}")
        rp_logger.debug(f"Query error: {error}")
        assert success, f"Failed to execute psql query: {error}"
        assert "Greenplum" in output, "Greenplum version not found in output"
        # Log the query result
        rp_logger.info(f"Query result: {output}")