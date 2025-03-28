import paramiko
import logging

logger = logging.getLogger(__name__)

class SSHConnection:
    def __init__(self, host=None, username=None, password=None, greenplum_clients_path=None):
        from . import config

        self.host = host or config.CLIENT_HOST
        self.username = username or config.CLIENT_USERNAME
        self.password = password or config.CLIENT_PASSWORD

        # Default path for Greenplum clients, can be overridden in config or passed directly
        self.greenplum_clients_path = greenplum_clients_path or getattr(config, 'GREENPLUM_CLIENTS_PATH',
                                                                        '/usr/local/greenplum-db-clients-7.4.0/greenplum_clients_path.sh')

        self.client = None
        self.sftp = None

    def connect(self):
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password
            )
            logger.info(f"SSH connection established to {self.host}")
            return True
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            return False

    def execute_command(self, command, timeout=60):
        """
        Execute a command on the remote system with Greenplum client path sourced

        Args:
            command (str): Command to execute
            timeout (int, optional): Command execution timeout. Defaults to 60 seconds.

        Returns:
            tuple: (success, output, error)
        """
        if not self.client:
            self.connect()

        try:
            # Construct full command that sources Greenplum client path
            full_command = f"""
                source {self.greenplum_clients_path} && 
                {command}
            """

            logger.info(f"Executing command: {full_command}")
            stdin, stdout, stderr = self.client.exec_command(full_command, timeout=timeout)

            # Read output
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            # Check command success
            success = stdout.channel.recv_exit_status() == 0

            logger.debug(f"Command output: {output}")
            if error:
                logger.warning(f"Command error: {error}")

            return success, output, error
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False, "", str(e)

    def check_greenplum_status(self):
        """Check if Greenplum is running on the target database host"""
        from . import config

        # Modify this command to check Greenplum status on the target database host
        check_command = f"psql -h {config.HOST} -U {config.USERNAME} -c 'SELECT version()'"
        success, output, error = self.execute_command(check_command)

        return success and "Greenplum" in output

    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            logger.info("SSH connection closed")
            self.client = None