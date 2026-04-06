import serial
from serial.tools import list_ports

ports = list_ports.comports()
TEST_BAUD = 115200

for i, port in enumerate(ports):
    print(f"[{i+1}]: {port.name}")

selection = input("Select port: ")

try:
    port_index = int(selection) - 1
    port = ports[port_index]

except:
    print(f"Unknown choice: {selection}")
    exit()

print(f"Selected {port.name}")

with serial.Serial(port.device, TEST_BAUD) as ser:
    while True:
        print(ser.readline().decode().strip())

