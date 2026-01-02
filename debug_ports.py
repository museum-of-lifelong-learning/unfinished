import serial
import time
import glob

def probe_port(port):
    print(f"--- Probing {port} ---")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"Opened {port}")
    except Exception as e:
        print(f"Failed to open {port}: {e}")
        return

    # 1. Try Display Probe (STATUS)
    print("Sending STATUS...")
    time.sleep(2) # Wait for potential reset
    ser.reset_input_buffer()
    ser.write(b"STATUS\n")
    time.sleep(0.5)
    resp = ser.read_all()
    print(f"Response to STATUS: {resp}")
    
    if b"OK PATTERN=" in resp:
        print("=> IDENTIFIED AS DISPLAY")
        ser.close()
        return

    # 2. Try RFID Probe (Get Version)
    # Cmd: BB 00 03 00 01 00 04 7E
    print("Sending RFID GetVersion...")
    cmd = bytearray([0xBB, 0x00, 0x03, 0x00, 0x01, 0x00, 0x04, 0x7E])
    ser.write(cmd)
    time.sleep(0.5)
    resp = ser.read_all()
    print(f"Response to RFID Cmd: {resp.hex().upper()}")
    
    if resp and resp[0] == 0xBB:
         print("=> IDENTIFIED AS RFID")
    else:
         print("=> UNKNOWN DEVICE")

    ser.close()

ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
print(f"Found ports: {ports}")

for port in ports:
    probe_port(port)
