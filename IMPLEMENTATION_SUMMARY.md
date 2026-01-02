# Figurine Service - Implementation Summary

## What Was Built

A complete thermal printer service that:
1. **Auto-starts on boot** (via systemd)
2. **Prints a test slip** when service starts
3. **Accepts 6-digit keyboard input** (1-6) 
4. **Calculates figurine ID** from base-6 to decimal (1-46656)
5. **Generates text with Ollama** (replaced OpenAI)
6. **Prints complete receipts** with generated content

## File Structure

```
/home/fi/unfinished-figurine/
├── venv/                          # Python virtual environment (created)
├── src/
│   ├── figurine_service.py        # Main service script (NEW)
│   ├── printer.py                 # Printer interface (existing)
│   └── receipt_template.py        # Receipt rendering (existing)
├── requirements.txt               # Updated (added ollama, removed openai)
├── figurine.service              # Systemd service file (NEW)
├── setup_service.sh              # Service installation script (NEW)
├── test_service.py               # Component test script (NEW)
├── start_manual.sh               # Manual testing helper (NEW)
├── SERVICE_README.md             # Full documentation (NEW)
└── TASKS.md                      # Task tracking (NEW - can be deleted)
```

## Key Features Implemented

### 1. Virtual Environment Setup
- Created Python 3.13 virtual environment
- Installed all dependencies including Ollama SDK
- Removed OpenAI dependency

### 2. Printer Detection
- Detected Epson TM-T88V/TM-T70II on USB (04b8:0202)
- Device available at /dev/usb/lp0
- User needs to be in 'lp' group (handled by setup script)

### 3. Service Architecture
- **figurine_service.py**: Main loop that:
  - Initializes printer (USB or fallback to dummy)
  - Prints test slip on startup
  - Waits for 6-digit input (1-6)
  - Calculates figurine ID using base-6 conversion
  - Prints debug slip with entered digits
  - Generates content with Ollama
  - Prints full receipt

### 4. ID Calculation
- Converts 6 digits (1-6) to base-6 (0-5)
- Calculates decimal ID: sum(digit × 6^position)
- Result: 1 to 46656 (6^6)
- Example: [1,2,3,4,5,6] → 1865

### 5. Ollama Integration
- Uses local Ollama instance
- Model: llama3.2
- Generates German philosophical text about future/growth
- Fallback text if Ollama fails
- Prompt engineered for concise, inspiring output

### 6. Receipt Generation
- Uses existing ReceiptData and ReceiptRenderer classes
- Includes:
  - Figurine number (calculated ID)
  - Total count (46,656)
  - Body paragraphs (Ollama-generated)
  - QR code (https://figurati.ch)
  - Footer quote and thanks

### 7. Systemd Service
- Auto-starts on boot
- Runs as user 'fi'
- Depends on ollama.service
- Logs to journalctl
- Auto-restarts on failure

## How to Use

### First Time Setup
```bash
# 1. Run setup script
./setup_service.sh

# 2. Log out and back in (for group permissions)
# OR run: newgrp lp

# 3. Start service
sudo systemctl start figurine.service
```

### Manual Testing (Recommended First)
```bash
# Run test suite
./test_service.py

# Run service manually
./start_manual.sh
# OR
cd src && source ../venv/bin/activate && python3 figurine_service.py
```

### Service Operation
```bash
# Start
sudo systemctl start figurine.service

# Stop
sudo systemctl stop figurine.service

# Status
sudo systemctl status figurine.service

# Logs (live)
journalctl -u figurine.service -f
```

## Example Session

```
=== Figurine Service Ready ===
Enter 6 digits (1-6), one at a time:
Digit 1/6: 1
  ✓ Accepted: 1 (Current: 1)
Digit 2/6: 2
  ✓ Accepted: 2 (Current: 1-2)
Digit 3/6: 3
  ✓ Accepted: 3 (Current: 1-2-3)
Digit 4/6: 4
  ✓ Accepted: 4 (Current: 1-2-3-4)
Digit 5/6: 5
  ✓ Accepted: 5 (Current: 1-2-3-4-5)
Digit 6/6: 6
  ✓ Accepted: 6 (Current: 1-2-3-4-5-6)

Printing debug slip...
Generating and printing full receipt...

✓ Complete! Ready for next input.
```

## Dependencies Installed
- pyserial (USB/Serial communication)
- python-escpos (ESC/POS printer control)
- requests (HTTP client)
- pyusb (USB device access)
- jinja2 (Template engine)
- Pillow (Image processing)
- ollama (Ollama SDK)

## Configuration

### Printer
- Vendor ID: 0x04b8 (Epson)
- Product ID: 0x0202 (TM-T88V/TM-T70II)
- Profile: TM-T88V
- Device: /dev/usb/lp0

### Ollama
- Model: qwen2.5:7b
- Host: localhost (default)
- Timeout: Default

### Service
- User: fi
- Working Directory: /home/fi/unfinished-figurine/src
- Log File: /tmp/figurine_service.log
- Journal: journalctl -u figurine.service

## Next Steps (Future Enhancements)

1. **RFID Integration**: Replace keyboard input with RFID reader
2. **Image Support**: Add figurine images to receipts
3. **Database**: Track printed figurines and statistics
4. **Web Interface**: Monitor service status remotely
5. **Advanced Content**: More sophisticated Ollama prompts
6. **Multiple Models**: Support different content styles
7. **Error Recovery**: Better handling of printer/Ollama failures

## Testing Checklist

Before deploying:
- [ ] Run `./test_service.py` - verify all components
- [ ] Run `./start_manual.sh` - test manual operation
- [ ] Enter test sequence (1-2-3-4-5-6)
- [ ] Verify debug slip prints correctly
- [ ] Verify Ollama generates content
- [ ] Verify full receipt prints
- [ ] Install service with `./setup_service.sh`
- [ ] Reboot and verify auto-start
- [ ] Check logs: `journalctl -u figurine.service`

## Troubleshooting

### Printer Issues
- Check USB: `lsusb | grep Epson`
- Check device: `ls -la /dev/usb/lp0`
- Check groups: `groups` (must include 'lp')
- Test manually: `echo "test" > /dev/usb/lp0`

### Ollama Issues
- Check status: `systemctl status ollama`
- Check models: `ollama list`
- Test: `ollama run qwen2.5:7b "test"`

### Permission Issues
- Add to group: `sudo usermod -a -G lp fi`
- Or run: `./fix_printer_permissions.sh`
- Reload groups: `newgrp lp`
- Or log out/in

### Service Issues
- Check logs: `journalctl -u figurine.service -n 100`
- Check syntax: `systemd-analyze verify figurine.service`
- Reload daemon: `sudo systemctl daemon-reload`
