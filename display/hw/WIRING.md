# Wiring Diagram: Xiao ESP32-C6 to MAX7219 LED Matrix

## Components
- **Microcontroller**: Seeed Xiao ESP32-C6
- **Display**: 4x MAX7219 8x8 LED Matrix modules (32x8 total)

## Pin Connections

### Xiao ESP32-C6 to MAX7219

| ESP32-C6 Pin | Function | MAX7219 Pin | Wire Color (suggested) |
|--------------|----------|-------------|------------------------|
| GPIO 10      | MOSI     | DIN         | Yellow                 |
| GPIO 8       | SCK      | CLK         | Orange                 |
| GPIO 9       | CS       | CS/LOAD     | Green                  |
| 5V           | Power    | VCC         | Red                    |
| GND          | Ground   | GND         | Black                  |

## Wiring Diagram (ASCII)

```
Xiao ESP32-C6                    MAX7219 Module Chain
┌─────────────┐                 ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│             │                 │  #1  │  │  #2  │  │  #3  │  │  #4  │
│     5V  ────┼─────────────────┤ VCC  ├──┤ VCC  ├──┤ VCC  ├──┤ VCC  │
│             │                 │      │  │      │  │      │  │      │
│     GND ────┼─────────────────┤ GND  ├──┤ GND  ├──┤ GND  ├──┤ GND  │
│             │                 │      │  │      │  │      │  │      │
│ GPIO 10 ────┼─────────────────┤ DIN  │  │      │  │      │  │      │
│    (MOSI)   │                 │      │  │      │  │      │  │      │
│             │                 │ DOUT ├──┤ DIN  │  │      │  │      │
│             │                 │      │  │ DOUT ├──┤ DIN  │  │      │
│             │                 │      │  │      │  │ DOUT ├──┤ DIN  │
│             │                 │      │  │      │  │      │  │      │
│ GPIO 8  ────┼─────────────────┤ CLK  ├──┤ CLK  ├──┤ CLK  ├──┤ CLK  │
│    (SCK)    │                 │      │  │      │  │      │  │      │
│             │                 │      │  │      │  │      │  │      │
│ GPIO 9  ────┼─────────────────┤ CS   ├──┤ CS   ├──┤ CS   ├──┤ CS   │
│    (CS)     │                 └──────┘  └──────┘  └──────┘  └──────┘
└─────────────┘
```

## Important Notes

1. **Power Supply**: 
   - The MAX7219 modules can draw significant current when all LEDs are on
   - If you experience issues, use an external 5V power supply for the LED modules
   - Connect external GND to ESP32-C6 GND (common ground)

2. **Module Chaining**:
   - Data flows from Module 1 → Module 2 → Module 3 → Module 4
   - DIN connects only to Module 1
   - DOUT of each module connects to DIN of the next module
   - CLK and CS are parallel across all modules

3. **Pin Selection**:
   - The default SPI pins for ESP32-C6 are being used
   - If you need to change pins, modify the definitions in `main.cpp`:
     ```cpp
     #define CLK_PIN   8  // SCK
     #define DATA_PIN  10 // MOSI
     #define CS_PIN    9  // CS
     ```

4. **Hardware Type**:
   - The code uses `MD_MAX72XX::FC16_HW` as the hardware type
   - If your display orientation is wrong, try these alternatives:
     - `MD_MAX72XX::PAROLA_HW`
     - `MD_MAX72XX::GENERIC_HW`
     - `MD_MAX72XX::ICSTATION_HW`

## Testing

1. Connect everything according to the diagram above
2. Connect the Xiao ESP32-C6 to your computer via USB
3. Build and upload the code using PlatformIO
4. Open the Serial Monitor (115200 baud) to see test progress
5. The LED matrix will cycle through different test patterns

## Troubleshooting

- **No LEDs light up**: Check power connections and ensure 5V is reaching the modules
- **Some modules don't work**: Verify the daisy-chain connections (DOUT → DIN)
- **Wrong orientation**: Change the `HARDWARE_TYPE` in main.cpp
- **Dim LEDs**: Adjust brightness by changing the intensity value (0-15) in setup()

## Serial Command API (USB)

Commands are newline-terminated. Responses start with `OK` or `ERR`.

- `PATTERN BORED` — slow abstract animation
- `PATTERN THINKING` — shows `OH!`, then `HI` rises, then loops scrolling `thinking`
- `PATTERN FINISH` — shows `THIS IS IT`, then one `BYE` scrolls, then clears
- `STOP` — stop any pattern and clear
- `SPEED <0-10>` — animation speed (0 slow, 10 fast)
- `BRIGHT <0-15>` — display brightness
- `STATUS` — report current pattern, speed, brightness
- `HELP` — list commands

### Python usage example (pyserial)

```python
import serial, time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

def send(cmd):
   ser.write((cmd + "\n").encode())
   resp = ser.readline().decode(errors='ignore').strip()
   print(cmd, '->', resp)

send('HELP')
send('BRIGHT 8')
send('SPEED 4')
send('PATTERN THINKING')
time.sleep(6)
send('PATTERN BORED')
time.sleep(5)
send('PATTERN FINISH')
time.sleep(4)
send('STOP')
ser.close()
```
