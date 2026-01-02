# Helper Tools

Utility scripts for testing and setup. Most users won't need these.

## Setup & Installation

- `install_udev_rules.sh` - Install printer USB access rules (run once)
- `fix_printer_permissions.sh` - Add user to lp group for printer access
- `verify_setup.sh` - Check if all requirements are met

## Testing

- `test_sequences.sh` - Send test digit sequences to the service
- `run_test_with_permissions.sh` - Run test_service.py with proper permissions
- `test_tty1_input.sh` - Test sending input to tty1 (deprecated, use tty8)

## Usage

Most of these tools are called automatically by the main setup scripts in the parent directory. You typically don't need to run them manually.

For normal usage, use the scripts in the root directory:
- `./setup_service.sh` - Full service installation
- `./start_manual.sh` - Run service manually
- `./watch_service.sh` - Monitor the service
