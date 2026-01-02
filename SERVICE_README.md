# Figurine Service - Setup & Usage

## Running Options

The service can run in two modes:

### Option 1: Manual Mode (Simple)
Run interactively in your current terminal:
```bash
./start_manual.sh
```

### Option 2: Systemd Service (Auto-start on boot)
The service will run on `/dev/tty8` (virtual console 8) and wait for keyboard input there.

**Setup:**
```bash
./setup_service.sh
sudo systemctl start figurine.service
```

**To interact with the service:**
- Switch to TTY8: Press `Ctrl+Alt+F8` (on physical console)
- Or via SSH: `sudo screen /dev/tty8` or view with `sudo cat /dev/vcs8`
- Switch back to GUI: `Ctrl+Alt+F7` (or F1/F2)

## Quick Setup

1. **Install dependencies:**
   ```bash
   cd /home/fi/unfinished-figurine
   source venv/bin/activate  # Already created
   ```

2. **Fix printer permissions:**
   ```bash
   ./install_udev_rules.sh
   ```

3. **Choose how to run:**

   **Manual mode:**
   ```bash
   ./start_manual.sh
   ```

   **Auto-start service (runs on tty1):**
   ```bash
   ./setup_service.sh
   sudo systemctl start figurine.service
   # Switch to tty1 with Ctrl+Alt+F1 to interact
   ```

## Running the Service

### Manual Mode (Easiest)

```bash
./start_manual.sh
```

This will:
- Activate the virtual environment
- Start the service with proper printer permissions
- Wait for keyboard input
- Print test slip on startup

## How It Works

1. **Service starts** and prints a test slip
2. **Waits for input**: Enter 6 digits (1-6), one at a time
3. **Calculates ID**: Converts base-6 to decimal (1-46656)
4. **Prints debug slip**: Shows entered digits and calculated ID
5. **Generates content**: Uses Ollama to create philosophical text
6. **Prints receipt**: Full receipt with generated content
7. **Loops**: Ready for next input

## Example Input

```
Digit 1/6: 1
Digit 2/6: 2
Digit 3/6: 3
Digit 4/6: 4
Digit 5/6: 5
Digit 6/6: 6
```

This translates to figurine ID: **1865** / 46656

## Service Commands

```bash
# Start service
sudo systemctl start figurine.service

# Stop service
sudo systemctl stop figurine.service

# Restart service
sudo systemctl restart figurine.service

# Check status
sudo systemctl status figurine.service

# View logs (live)
journalctl -u figurine.service -f

# View all logs
journalctl -u figurine.service

# Disable auto-start
sudo systemctl disable figurine.service

# Enable auto-start
sudo systemctl enable figurine.service
```

## Troubleshooting

### Printer not found
- Check USB connection: `lsusb | grep Epson`
- Verify printer device: `ls -la /dev/usb/lp0`
- Check user groups: `groups` (should include 'lp')
- Fix permissions: `./fix_printer_permissions.sh` then log out/in

### Ollama not working
- Check if Ollama is running: `systemctl status ollama`
- Test Ollama: `ollama run qwen2.5:7b "test"`
- Check model availability: `ollama list`

### Service won't start
- Check logs: `journalctl -u figurine.service -n 50`
- Verify virtual environment: `source venv/bin/activate && python3 -c "import ollama"`
- Check permissions: Service runs as user 'fi'

## Files

**Main Scripts:**
- `start_manual.sh` - Run service manually (recommended)
- `watch_service.sh` - Monitor service (tty8 + logs)
- `tail_logs.sh` - Live log stream
- `view_tty8.sh` - View current tty8 screen
- `setup_service.sh` - Install systemd service
- `test_service.py` - Test all components

**Service Files:**
- `src/figurine_service.py` - Main service script
- `src/printer.py` - Printer interface
- `src/receipt_template.py` - Receipt rendering
- `figurine.service` - Systemd service file
- `run_service_wrapper.sh` - Service wrapper (internal)

**Utilities:**
- `tools/` - Additional helper scripts (setup, testing)

**Logs:**
- `/tmp/figurine_service.log` - Service log file
- `journalctl -u figurine.service` - System logs

## Ollama Configuration

The service uses Ollama with the `qwen2.5:7b` model. The model should already be available:

```bash
# Verify model is available
ollama list

# Test it
ollama run qwen2.5:7b "Hello"
```

## Next Steps (Future)

- [ ] Integrate RFID reader instead of keyboard input
- [ ] Add image generation/selection for receipts
- [ ] Create web interface for monitoring
- [ ] Add database for tracking printed figurines
