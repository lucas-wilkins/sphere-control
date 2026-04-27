import logging
import socket
import struct
import time
from typing import Callable

from configuration import config

class ControlCommand:
    """ Command to be sent over TCP """

    _has_stage = 1
    _has_sphere = 2
    _has_lights = 4
    _do_wait = 8

    def __init__(self, stage_steps: int | None, sphere_steps: int | None, light_command: bytes | None, wait=True):
        self.stage_steps = stage_steps
        self.sphere_steps = sphere_steps
        self.light_command = light_command
        self.wait = wait

    def to_bytes(self):
        """ Convert to bytes to be sent """

        flags = 0
        data_section = bytearray()

        if self.stage_steps is not None:
            flags |= ControlCommand._has_stage
            data_section += self.stage_steps.to_bytes(4, byteorder='little', signed=True)

        if self.sphere_steps is not None:
            flags |= ControlCommand._has_sphere
            data_section += self.sphere_steps.to_bytes(4, byteorder='little', signed=True)

        if self.light_command is not None:
            flags |= ControlCommand._has_lights
            data_section += self.light_command

        if self.wait:
            flags |= ControlCommand._do_wait

        return flags.to_bytes(1, byteorder='little', signed=False) + data_section

    @staticmethod
    def from_bytes(data: bytes):
        """ Convert from bytes """
        contents_flags = int.from_bytes(data[:1], byteorder='little', signed=False)
        data = data[1:]

        # Stage axis
        if contents_flags & ControlCommand._has_stage:
            stage = int.from_bytes(data[:4], byteorder='little', signed=True)
            data = data[4:]

        else:
            stage = None

        # Sphere axis
        if contents_flags & ControlCommand._has_sphere:
            sphere = int.from_bytes(data[:4], byteorder='little', signed=True)
            data = data[4:]

        else:
            sphere = None

        # Lights
        if contents_flags & ControlCommand._has_lights:
            lights = data

        else:
            lights = None

        wait = bool(contents_flags & ControlCommand._do_wait)

        # Return
        return ControlCommand(stage, sphere, lights, wait)



    @staticmethod
    def from_degrees(stage_deg: float | None, sphere_deg: float | None, light_command: bytes | None):
        """ Specify using degrees """
        stage_steps = int(stage_deg * config.stage_steps_per_revolution / 360)
        sphere_steps = int(sphere_deg * config.sphere_steps_per_revolution / 360)

        return ControlCommand(stage_steps, sphere_steps, light_command)

    def __eq__(self, other: "ControlCommand"):
        if isinstance(other, ControlCommand):
            return self.stage_steps == other.stage_steps and \
                self.sphere_steps == other.sphere_steps and \
                self.light_command == other.light_command and \
                self.wait == other.wait
        else:
            return False

class ControlServer:
    def __init__(self,
                 stage_callback: Callable[[int], None],
                 sphere_callback: Callable[[int], None],
                 lights_callback: Callable[[bytes], None],
                 wait_callback: Callable[[], bool]):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.stage_callback = stage_callback
        self.sphere_callback = sphere_callback
        self.lights_callback = lights_callback
        self.wait_callback = wait_callback

        self.host = "0.0.0.0"
        self.port = config.control_server_port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1) # Single client

        self.logger.info(f"Control server listening on port {self.port}")

    def receive_exact(self, size):
        """Receive exactly `size` bytes."""
        data = b''

        while len(data) < size:
            packet = self.server.recv(size - len(data))

            if not packet:
                return None

            data += packet

        return data

    def receive_message(self):
        """ Receive a variable length message"""

        raw_length = self.receive_exact(4)

        if not raw_length:
            return None

        # Get the message length from the bytes
        message_length = struct.unpack('!I', raw_length)[0]

        # Read message body
        return self.receive_exact(message_length)

    def handle_client(self, client_socket, client_address):
        self.logger.info(f"Connected: {client_address}")

        try:
            while True:
                data = self.receive_message()

                if not data:
                    break

                self.on_message(data)
                #client_socket.sendall(b"Message received")

        except Exception as e:
            self.logger.error(f"Error with {client_address}: {e}")

        finally:
            client_socket.close()
            self.logger.info(f"Disconnected: {client_address}")

    def send_done(self):
        pass

    def on_message(self, data: bytes):
        command = ControlCommand.from_bytes(data)

        do_wait = False
        if command.light_command is not None:
            self.lights_callback(command.light_command)

        if command.stage_steps is not None:
            self.stage_callback(command.stage_steps)
            do_wait |= True

        if command.sphere_steps is not None:
            self.sphere_callback(command.sphere_steps)
            do_wait |= True

        if do_wait and command.wait:
            while not self.wait_callback():
                time.sleep(0.1)

        self.send_done()

if __name__ == "__main__":
    cc = ControlCommand(1,2,bytes([1,2,3]))
    encoded = cc.to_bytes()


