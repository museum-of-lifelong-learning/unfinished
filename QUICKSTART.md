# Figurine Service - Quick Start

## Running the Service

**Manual Mode (easiest):**
```bash
./start_manual.sh
```

**Monitor the service:**
```bash
./watch_service.sh    # Live view of tty8 + logs
./tail_logs.sh        # Live log stream only
./view_tty8.sh        # Quick tty8 snapshot
```

## Features

✅ Random figurine image generation (unique per ID)
✅ AI-generated personalized content (Ollama)
✅ Complete receipt with all fields
✅ Keyboard input on tty8 (Ctrl+Alt+F8)
✅ Detailed timing logs

## Structure

```
/home/fi/unfinished-figurine/
├── start_manual.sh          # START HERE - Run service
├── watch_service.sh         # Monitor service
├── tail_logs.sh             # View logs
├── view_tty8.sh             # Check tty8
├── setup_service.sh         # Install systemd service
├── test_service.py          # Test components
├── src/                     # Main code
│   ├── figurine_service.py  # Service logic
│   ├── printer.py           # Printer interface
│   └── receipt_template.py  # Receipt rendering
├── scripts/                 # Generators
│   └── generate_figurine_png.py
├── tools/                   # Utilities (rarely needed)
└── assets/                  # Generated figurines

```

## How It Works

1. Press Ctrl+Alt+F8 on physical keyboard
2. Enter 6 digits (1-6)
3. Service generates:
   - Random figurine image (reproducible per ID)
   - AI content with Ollama
   - Complete receipt
4. Prints to thermal printer
5. Ready for next input

See SERVICE_README.md for full documentation.
