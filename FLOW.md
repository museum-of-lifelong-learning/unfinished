# Figurine Service Flow

This document outlines the interaction flow between the RFID reader, LED Display, and Thermal Printer.

## Components
- **RFID Reader**: M5Stack U107 UHF RFID Reader (Serial/USB)
- **Display**: LED Matrix controlled by ESP32 (Serial/USB)
- **Printer**: Thermal Printer (USB/Serial)
- **Service**: Python script orchestrating the components

## States & Flow

### 1. Initialization
- Service starts.
- **Auto-detection**: Service scans for connected devices (RFID, Display, Printer).
- **Status Output**: Service prints the status of connected devices to the console/logs.
- **Initial State**:
    - Display: `PATTERN BORED`
    - RFID: Start scanning
    - Printer: Idle

### 2. Bored / Scanning Mode
- **Display**: Shows "Bored" animation.
- **RFID**: Continuously scans for tags.
- **Condition**: Wait until **6 unique tags** are detected.

### 3. Thinking / Processing Mode
- **Trigger**: 6 tags detected.
- **Action**:
    - **Display**: Switch to `PATTERN THINKING`.
    - **RFID**: Stop/Pause scanning.
    - **Service**:
        - Extract IDs from the 6 tags.
        - Generate content (text/image) based on the IDs (using Ollama/Templates).

### 4. Printing / Finish Mode
- **Action**:
    - **Printer**: Print the generated receipt/content.
    - **Display**: Switch to `PATTERN FINISH`.
- **Duration**: Wait for printing to complete or a set duration (e.g., 5-10 seconds).

### 5. Reset
- **Action**:
    - Clear internal state (detected tags).
    - **Display**: Switch back to `PATTERN BORED`.
    - **RFID**: Resume scanning.
