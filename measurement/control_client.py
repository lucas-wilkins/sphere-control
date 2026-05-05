import socket

from control_server import ControlCommand
from light_commands import SingleLight
from spherecontrol.configuration import config

class ControlClient:
    def __init__(self, address: str = "127.0.0.1"):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, config.control_server_port))

    def send(self, msg: ControlCommand):
        message_bytes = msg.to_bytes()
        n_bytes = len(message_bytes)
        length_bytes = n_bytes.to_bytes(4, byteorder='little', signed=False)
        self.socket.sendall(length_bytes + message_bytes)


    def close(self):
        self.socket.close()

if __name__ == "__main__":
    import time
    client = ControlClient()
    for i in range(5):
        client.send(ControlCommand(i, 30, SingleLight(10).serial_command))
        time.sleep(1)

