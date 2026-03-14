import logging
import serial

from firmware.lights.light_messages import LightMessageType
from test_sequences.axis_sequence import AxisSequence
from test_sequences.base_sequence import TestSequenceSeries
from test_sequences.chase_sequence import ChaseSequence
from test_sequences.rainbow import Rainbows

LIGHTS_BAUD = 9600
MOTOR_BAUD = 9600

class SerialControl:
    """ Main class for handling serial communication with all devices """
    def __init__(self,
                 stage_port ="dummy",
                 sphere_port ="dummy",
                 lights_port = "dummy"):

        self.lights_serial = DummyLightSerial() if lights_port == "dummy" else serial.Serial(lights_port, LIGHTS_BAUD)
        self.stage_serial = DummyMotorSerial() if stage_port == "dummy" else serial.Serial(stage_port, MOTOR_BAUD)
        self.sphere_serial = DummyMotorSerial() if sphere_port == "dummy" else serial.Serial(sphere_port, MOTOR_BAUD)

        self.is_homed = False


class DummySerial:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.byte_queue: bytearray = bytearray()

    def write(self, msg: bytes):
        self.logger.info(msg)

    @property
    def in_waiting(self) -> int:
        return len(self.byte_queue)

    def read(self) -> bytes:
        data = bytes(self.byte_queue)
        self.byte_queue = bytearray()
        return data

    def _enqueue(self, msg: bytes):
        self.byte_queue += msg

class DummyLightSerial(DummySerial):

    def write(self, msg: bytes):
        super().write(msg)

        assert len(msg) > 0, "Don't send empty messages to serial"

        match LightMessageType(int(msg[0])):
            case LightMessageType.IDENTIFY:
                self._enqueue(bytes([LightMessageType.IDENTIFY.value, 1]))

            case LightMessageType.SINGLE_LIGHT:
                self.logger.info("Single Light Request")

            case LightMessageType.SINGLE_LIGHT_COLOR:
                self.logger.info("Single Light Request (Colour)")

            case LightMessageType.FULL_LIGHT_SPEC:
                self.logger.info("Full State Request")

            case _:
                self._enqueue(bytes([LightMessageType.UNKNOWN_REQUEST.value]))

class DummyMotorSerial(DummySerial):

    def write(self, msg: bytes):
        super().write(msg)