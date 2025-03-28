import logging
from utils import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestPgDump:
    """Tests for core Greenplum client tools"""

    def test_pg_dump_restore(self, ssh_connection, test_database, unique_name, rp_logger):
        """Test pg_dump and pg_restore functionality"""
        # Create a test table and insert data
        table_name = f"test_table_{unique_name}"
        create_table_query = f"CREATE TABLE {table_name} (id INT, name TEXT);"
        insert_query = f"INSERT INTO {table_name} VALUES (1, 'Test');"

        rp_logger.info(f"Creating test table {table_name} in database {test_database}")
        ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -d {test_database} -c \"{create_table_query}\""
        )

        rp_logger.info(f"Inserting test data into table {table_name}")
        ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -d {test_database} -c \"{insert_query}\""
        )

        # Test pg_dump
        dump_file = f"/tmp/dump_{unique_name}.sql"
        rp_logger.info(f"Testing pg_dump with database: {test_database} to file: {dump_file}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && pg_dump -h {config.HOST} -U {config.USERNAME} -f {dump_file} {test_database}"
        )
        rp_logger.debug(f"pg_dump output: {output}")
        rp_logger.debug(f"pg_dump error: {error}")
        assert success, f"Failed to dump database: {error}"

        # Verify dump file exists
        rp_logger.info(f"Verifying dump file exists: {dump_file}")
        success, output, error = ssh_connection.execute_command(f"ls -l {dump_file}")
        rp_logger.debug(f"File check output: {output}")
        assert success, f"Dump file {dump_file} not found"

        # Verify "Greenplum Database database dump complete" message in dump file
        rp_logger.info("Checking for Greenplum Database dump complete message")
        success, output, error = ssh_connection.execute_command(
            f"grep -q 'Greenplum Database database dump complete' {dump_file}"
        )
        rp_logger.debug(f"Dump message verification output: {output}")
        rp_logger.debug(f"Dump message verification error: {error}")
        assert success, "Greenplum Database dump complete message not found in dump file"

        # Create a new database for restore
        restore_db = f"restore_db_{unique_name}"
        rp_logger.info(f"Creating restore database: {restore_db}")
        ssh_connection.execute_command(
            f"source ~/.bashrc && createdb -h {config.HOST} -U {config.USERNAME} {restore_db}"
        )

        # Test restore
        rp_logger.info(f"Testing restore with dump file: {dump_file} to database: {restore_db}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -d {restore_db} -f {dump_file}"
        )
        rp_logger.debug(f"Restore output: {output}")
        rp_logger.debug(f"Restore error: {error}")
        assert success, f"Failed to restore database: {error}"

        # Verify data exists in restored database
        rp_logger.info(f"Verifying data in restored database: {restore_db}")
        success, output, error = ssh_connection.execute_command(
            f"source ~/.bashrc && psql -h {config.HOST} -U {config.USERNAME} -d {restore_db} -t -c \"SELECT count(*) FROM {table_name}\""
        )
        rp_logger.debug(f"Verification output: {output}")
        assert success and "1" in output, "Data not found in restored database"
        rp_logger.info("Data successfully restored")

        # Clean up
        rp_logger.info("Cleaning up test artifacts")
        ssh_connection.execute_command(f"rm -f {dump_file}")
        ssh_connection.execute_command(
            f"source ~/.bashrc && dropdb -h {config.HOST} -U {config.USERNAME} {restore_db}"
        )