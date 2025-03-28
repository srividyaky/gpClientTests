# Greenplum Client Tests Framework

## Overview
This pytest-based framework provides comprehensive testing for Greenplum client tools across different platforms (Rocky 8 and Rocky 9). The framework is designed to validate core Greenplum database client functionalities through automated tests.

## Prerequisites

### System Requirements
- Python 3.9+
- Greenplum Database Clients (version 7.4.0)
- SSH access to target client and database hosts

### Python Dependencies
Install the required dependencies using:
```bash
pip3 install -r requirements.txt
```

## Configuration

### Platform Configuration
The framework uses `utils/platform_config.json` to manage connection details for different platforms:
- Supports Rocky 8 and Rocky 9 configurations
- Defines client and database host credentials
- Allows environment-specific settings

### Environment Variables
Key environment variables:
- `GPDB_PLATFORM`: Specify target platform (rocky8/rocky9)
- `GPDB_CLIENT_HOST`: Override client host
- `GPDB_CLIENT_USERNAME`: Override client username
- `GPDB_CLIENT_PASSWORD`: Override client password
- `GPDB_HOST`: Override database host
- `GPDB_USERNAME`: Override database username
- `GPDB_PASSWORD`: Override database password

## Running Tests

### Local Test Execution
```bash
# For Rocky 8
GPDB_PLATFORM=rocky8 pytest -xvs --reportportal

# For Rocky 9
GPDB_PLATFORM=rocky9 pytest -xvs --reportportal
```

### Test Suites
The framework includes tests for:
- Database Creation/Deletion
- User Creation/Deletion
- PostgreSQL Dump and Restore
- Basic PSQL Queries

## Logging
- Logs are stored in the `logs/test_run.log` file
- Configurable log levels via `LOG_LEVEL` environment variable
- Integrated with Report Portal for enhanced test reporting

## Report Portal Integration
- Endpoint: http://10.84.94.199:8080
- Project: greenplum
- Provides detailed test execution reports
- Configurable launch attributes and descriptions

## Project Structure
```
gpClientTests/
├── README.md
├── conftest.py          # Pytest fixtures and configuration
├── logs/                # Log files directory
├── pytest.ini           # Report Portal and pytest configurations
├── requirements.txt     # Python dependencies
├── test_data/           # Additional test data
├── tests/               # Test modules
│   ├── test_createdb_dropdb.py
│   ├── test_createuser_dropuser.py
│   ├── test_pgdump_pgrestore.py
│   └── test_psql.py
└── utils/               # Utility modules
    ├── config.py        # Configuration management
    ├── helpers.py       # Helper functions
    ├── platform_config.json  # Platform-specific configurations
    └── ssh_utils.py     # SSH connection utilities
```

## Troubleshooting
- Ensure SSH connectivity to client and database hosts
- Verify Greenplum client paths
- Check network and firewall settings
- Validate credentials in `platform_config.json`

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add/modify tests
4. Run tests locally
5. Submit a pull request
