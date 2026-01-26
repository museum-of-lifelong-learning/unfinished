# Figurine Interaction System

An interactive museum installation for "Unfinished by Design - The Museum of Lifelong Learning". Visitors collect 6 RFID-tagged tokens that represent their learning mindset, needs, and situation. The system generates a unique "Lerncharakter" (learning character) figurine and personalized philosophical text printed on a thermal receipt.

## Features

-   **RFID Identification**: Detects 6 unique items using UHF RFID tags (M5Stack U107).
-   **Interactive Display**: Visual feedback via 4x8 LED matrix (ESP32-controlled) with animated states (Snake, Thinking, Text scrolling).
-   **AI Content Generation**: Uses Google Gemini API to generate personalized, empathetic German text based on visitor's learning profile.
-   **Figurine Generation**: Creates unique SVG-based geometric figurines from 27,000 possible combinations.
-   **Thermal Printing**: Prints receipts with figurine image, AI-generated text, resource recommendations, and QR code.
-   **Data Persistence**: Uploads slip data to Supabase with offline fallback support.
-   **Web Gallery**: Companion web app to view and explore all figurine variations.
-   **Automated Service**: Runs as a systemd service for auto-start on boot.

## Hardware Setup

### Controller
-   **Device**: HP Mini or Raspberry Pi 5
-   **OS**: Linux (Debian/Ubuntu based)

### RFID System
-   **Reader**: [M5Stack U107 UHF RFID Module](https://docs.m5stack.com/en/unit/uhf_rfid)
    -   Interface: USB/UART (115200 baud)
    -   Region: EU (865-868 MHz)
    -   Power: 26dBm
-   **Tags**: [NXP UCODE® 9 30mm | ISO18000-6C](https://www.rfidlabel.com/product/30mm-round-rfid-label/)

### Printer
-   **Model**: [Epson TM-T70II M296A](https://www.epson.ch/de_CH/produkte/drucker/bondrucker/pos-drucker/pc-pos-drucker/epson-tm-t70ii-series/p/12752)
-   **Type**: Thermal Receipt Printer (80mm paper, 512px width)
-   **Interface**: USB
-   **Profile**: TM-T88V compatible

### Display
-   **Hardware**: 4x MAX7219 8x8 LED Matrix modules (FC16 type)
-   **Controller**: ESP32/ESP8266
-   **Interface**: Serial/USB (115200 baud)
-   **Firmware**: PlatformIO project in `display/hw/`

## Software Setup

### Prerequisites
-   Python 3.11+
-   Google Gemini API key (for content generation)
-   Supabase account (for data persistence)
-   `lp` group access for printer

### Environment Variables

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_RPM_LIMIT=15
GEMINI_DAILY_LIMIT=1500
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
FIGURINE_OUTPUT_DIR=/path/to/output
```

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd figurine
    ```

2.  **Install dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Setup Printer Permissions**:
    ```bash
    ./tools/install_udev_rules.sh
    ```
    You may need to log out and back in for group changes to take effect.

4.  **Install Systemd Service** (for auto-start):
    ```bash
    ./tools/setup_service.sh
    sudo systemctl start figurine.service
    ```

5.  **Flash Display Firmware** (if using LED matrix):
    ```bash
    cd display/hw
    pio run --target upload
    ```

## Usage

### Manual Mode (Development)
To run the service interactively in your terminal:
```bash
./tools/start_manual.sh
```

Use `--no-print` flag to skip actual printing during development:
```bash
python3 src/figurine_service.py --no-print
```

### Service Mode (Production)
The service runs automatically on boot.
-   **Start**: `sudo systemctl start figurine.service`
-   **Stop**: `sudo systemctl stop figurine.service`
-   **Status**: `sudo systemctl status figurine.service`
-   **Logs**: `journalctl -u figurine.service -f`

### Testing Scripts
Located in `scripts/`:
-   `test_rfid_detection.py` - Test RFID reader connectivity
-   `test_receipt.py` - Test receipt printing
-   `test_gemini_api.py` - Test AI content generation
-   `test_display_states.py` - Test LED display patterns
-   `test_all_shapes.py` - Preview all figurine shapes
-   `register_rfid_tags.py` - Register new RFID tags to answers

## Workflow

1.  **Snake State**: The system waits for tokens with an animated snake pattern.
2.  **Scanning**: Detects and reads 6 RFID tags using anti-collision polling.
3.  **Thinking**: Display shows "THINKING" while:
    -   Tags are matched to answers from Excel data
    -   Unique Figurine ID is calculated (1 to 27,000)
    -   Gemini generates personalized text based on mindset, needs, and situation
    -   SVG figurine is generated and converted to PNG
4.  **Printing**: Display shows "VOILA" while the receipt prints with:
    -   Figurine image
    -   Two personalized paragraphs
    -   Resource recommendations (Tools, Locations, Programs)
    -   QR code linking to web gallery
5.  **Finish**: Display shows "THANK YOU!" and waits for token removal.

## Architecture

### Core Service
-   `src/figurine_service.py` - Main service orchestrator and state machine
-   `src/data_service.py` - Excel data handler for answers, resources, and prompts
-   `src/content_generation.py` - Gemini API interface with rate limiting
-   `src/slip_data_generation.py` - Generates all receipt content with offline fallback
-   `src/slip_printing.py` - Receipt layout and thermal printing

### Hardware Controllers
-   `src/rfid_controller.py` - M5Stack U107 UHF RFID interface
-   `src/display_controller.py` - Serial LED matrix controller
-   `src/printer_controller.py` - ESC/POS thermal printer interface

### Figurine Generation
-   `src/generate_figurine.py` - SVG figurine composition
-   `src/shapes.py` - Shape drawing library (40+ geometric shapes)

### Data & Upload
-   `src/supabase_upload.py` - Supabase database integration
-   `assets/Unfinished_data_collection.xlsx` - Answer and resource data
-   `assets/slip_content_fallback.csv` - Offline fallback content

### Web Gallery
-   `docs/` - Static web app for figurine gallery
-   `scripts/generate_web_svgs.py` - Generate all 27,000 figurine SVGs

### Display Firmware
-   `display/hw/` - PlatformIO project for ESP32 LED matrix controller

## Troubleshooting

-   **Printer not found**: Check USB connection and permissions (`lsusb`, `groups`). Ensure user is in `lp` group. Run `./tools/fix_printer_permissions.sh`.
-   **Gemini API error**: Check API key in `.env`. Verify rate limits (15 RPM, 1500/day for free tier). Check `/tmp/gemini_rate_limit.json` for usage.
-   **RFID not reading**: Check USB connection. Run `scripts/rfid_diagnostic.py`. Ensure EU region (865-868 MHz) is configured.
-   **Display not responding**: Check serial connection. Verify ESP32 firmware is flashed. Use `scripts/test_display_states.py`.
-   **Offline mode**: If no internet, system uses fallback CSV data automatically.

## Data Model

Each visitor's profile consists of:
-   **Mindsets**: Explorer, Experiencer, Sensemaker, Strategist
-   **Needs (F05)**: Learning requirements and barriers
-   **Situation (F06)**: Current life/work context

The system calculates a unique Figurine ID from the combination of 6 answers, mapping to one of 27,000 possible figurine configurations.
