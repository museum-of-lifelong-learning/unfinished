# Figurine Interaction System (RFID & Thermal Printer)

This project identifies objects using UHF RFID tags and generates a printed output based on the identified items using an LLM.

## Workflow

1.  **Selection**: User chooses 6 items (out of 36 available).
2.  **Identification**: User places the 6 items (each with a UHF RFID tag) over the antenna.
3.  **Recognition**: The system reads the tags to identify the items.
4.  **Processing**: An LLM (Remote or Local) generates text based on the identified items.
5.  **Output**: The generated text is printed on a thermal printer.

## Hardware Setup

### Controller
- **Device**: HP Mini or Raspberry Pi 5 (TBD)
- **OS**: Linux (Debian/Ubuntu based)

### RFID System
- **Reader**: [Rainy UHF RFID HAT for Raspberry Pi](https://shop.sb-components.co.uk/products/rainy-uhf-pi-hat-complete-kit)
    - Interface: USB / UART
    - Antenna: 3dBi
- **Tags**: [NXP UCODE® 9 30mm | ISO18000-6C](https://www.rfidlabel.com/product/30mm-round-rfid-label/)

### Printer
- **Model**: [Epson TM-T70II M296A](https://www.epson.ch/de_CH/produkte/drucker/bondrucker/pos-drucker/pc-pos-drucker/epson-tm-t70ii-series/p/12752)
- **Type**: Thermal Receipt Printer
- **Interface**: USB / Ethernet (TBD based on specific model variant)

## Software Stack

- **Language**: Python 3
- **Libraries**:
    - `pyserial`: For communicating with the RFID reader (if UART) or Printer.
    - `python-escpos`: For controlling the Epson thermal printer.
    - `requests` / `openai`: For LLM interaction.

## Setup & Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Application**:
    ```bash
    python src/main.py
    ```

## Development Status

- [x] Archive old visual recognition approach.
- [ ] RFID Reader integration (Skeleton implemented).
- [ ] Thermal Printer integration.
- [ ] LLM integration.
