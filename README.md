# Figurine Interaction System

This project identifies objects using UHF RFID tags and generates a printed output based on the identified items using an LLM. It orchestrates an RFID reader, an LED display, and a thermal printer to create an interactive experience.

## Features

-   **RFID Identification**: Detects 6 unique items using UHF RFID tags.
-   **Interactive Display**: Visual feedback via LED matrix (Bored, Thinking, Printing, Finished states).
-   **AI Content Generation**: Uses local LLM (Ollama) to generate personalized, philosophical content based on the combination of items.
-   **Thermal Printing**: Prints a high-quality receipt with a generated figurine image and the AI-generated text.
-   **Automated Service**: Runs as a systemd service for auto-start on boot.

## Hardware Setup

### Controller
-   **Device**: HP Mini or Raspberry Pi 5
-   **OS**: Linux (Debian/Ubuntu based)

### RFID System
-   **Reader**: [Rainy UHF RFID HAT for Raspberry Pi](https://shop.sb-components.co.uk/products/rainy-uhf-pi-hat-complete-kit) / M5Stack U107
    -   Interface: USB / UART
    -   Antenna: 3dBi
-   **Tags**: [NXP UCODE® 9 30mm | ISO18000-6C](https://www.rfidlabel.com/product/30mm-round-rfid-label/)

### Printer
-   **Model**: [Epson TM-T70II M296A](https://www.epson.ch/de_CH/produkte/drucker/bondrucker/pos-drucker/pc-pos-drucker/epson-tm-t70ii-series/p/12752)
-   **Type**: Thermal Receipt Printer
-   **Interface**: USB / Ethernet

### Display
-   **Device**: LED Matrix controlled by ESP32
-   **Interface**: Serial/USB

## Software Setup

### Prerequisites
-   Python 3.13+
-   Ollama (running locally)
-   `lp` group access for printer

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd unfinished-figurine
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
    ./setup_service.sh
    sudo systemctl start figurine.service
    ```

## Usage

### Manual Mode (Development)
To run the service interactively in your terminal:
```bash
./start_manual.sh
```

### Service Mode (Production)
The service runs automatically on boot.
-   **Start**: `sudo systemctl start figurine.service`
-   **Stop**: `sudo systemctl stop figurine.service`
-   **Status**: `sudo systemctl status figurine.service`
-   **Logs**: `journalctl -u figurine.service -f`

### Monitoring
-   **Watch Service**: `./watch_service.sh` (Live view of logs)
-   **Tail Logs**: `./tail_logs.sh`

## Workflow

1.  **Bored State**: The system waits for 6 unique RFID tags. Display shows "BORED".
2.  **Scanning**: As tags are detected, the display updates progress.
3.  **Thinking**: Once 6 tags are found, the system calculates a unique Figurine ID and generates content using Ollama. Display shows "THINKING".
4.  **Printing**: The receipt is printed. Display shows "PRINTING".
5.  **Finished**: The system waits for a few seconds before resetting. Display shows "FINISHED".

## Architecture

-   `src/figurine_service.py`: Main service orchestrator.
-   `src/figurine_id.py`: Logic for calculating Figurine ID from tags.
-   `src/content_generation.py`: Interface with Ollama for text generation.
-   `src/figure_generation.py`: Generates the figurine image.
-   `src/slip_printing.py`: Handles receipt layout and printing.
-   `src/display_controller.py`: Controls the LED matrix.
-   `src/printer.py`: Interface for the thermal printer.
-   `rfid/rfid_reader.py`: Interface for the RFID reader.

## Troubleshooting

-   **Printer not found**: Check USB connection and permissions (`lsusb`, `groups`). Ensure user is in `lp` group.
-   **Ollama error**: Ensure Ollama is running (`systemctl status ollama`) and the model is pulled (`ollama pull qwen2.5:3b`).
-   **RFID not reading**: Check connections and power to the reader.
