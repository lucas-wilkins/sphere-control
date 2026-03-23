from serial.tools import list_ports

if __name__ == "__main__":
    print(list_ports.comports())