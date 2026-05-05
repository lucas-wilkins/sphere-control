import logging
import socket
import time
from typing import Callable
import threading

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
                 is_moving_callback: Callable[[], bool]):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.stage_callback = stage_callback
        self.sphere_callback = sphere_callback
        self.lights_callback = lights_callback
        self.is_moving_callback = is_moving_callback

        self.host = "0.0.0.0"
        self.port = config.control_server_port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1) # Single client

        self._stop_event: threading.Event | None = None

    def receive_exact(self, size, client_socket):
        """Receive exactly `size` bytes."""
        data = b''

        while len(data) < size:
            packet = client_socket.recv(size - len(data))

            if not packet:
                return None

            data += packet

        return data

    def receive_message(self, client_socket):
        """ Receive a variable length message"""

        raw_length = self.receive_exact(4, client_socket)

        if not raw_length:
            return None

        # Get the message length from the bytes
        message_length =  int.from_bytes(raw_length, byteorder='little', signed=False)

        # Read message body
        return self.receive_exact(message_length, client_socket)

    def serve(self):
        self._stop_event = threading.Event()
        self._server_thread = threading.Thread(target=self._serve_outer_loop)
        self._server_thread.start()

    def shutdown(self):
        if self._stop_event is not None:
            self.logger.info("Shutting down control server")
            self._stop_event.set()

    def _serve_outer_loop(self):

        self.server.settimeout(1.0)

        self.logger.info(f"Control server listening on port {self.port}")
        while not self._stop_event.is_set():
            try:
                client_socket, client_address = self.server.accept()
            except TimeoutError:
                continue

            self.logger.info(f"Accepted connection from {client_address}")
            self.handle_client(client_socket, client_address)
            self.logger.info(f"Control server listening on port {self.port}")


        self.logger.info("Control server stopped")

    def handle_client(self, client_socket, client_address):
        self.logger.info(f"Connected: {client_address}")

        client_socket.settimeout(1.0)

        try:
            while not self._stop_event.is_set():
                data = self.receive_message(client_socket)

                if not data:
                    break

                self.on_message(data)
                #client_socket.sendall(b"Message received")

        except Exception as e:
            self.logger.error(f"Error communicating on {client_address}: {e}")

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
            while self.is_moving_callback():
                time.sleep(0.05)

        self.send_done()

if __name__ == "__main__":



    def motor_callback(motor_name: str):
        logger = logging.getLogger(motor_name)
        def callback(position):
            logger.info(f"{motor_name} callback: {position}")
        return callback

    wait_logger = logging.getLogger("Wait callback")
    def wait_callback():
        wait_logger.info("Wait for move")
        return False


    lights_logger = logging.getLogger("Lights callback")
    def lights_callback(msg: bytes):
        lights_logger.info(msg)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s, %(name)s: %(message)s"
    )

    server = ControlServer(
        stage_callback=motor_callback("Stage"),
        sphere_callback=motor_callback("Sphere"),
        lights_callback=lights_callback,
        is_moving_callback=wait_callback)

    server.serve()

    print("Main thread continues")


