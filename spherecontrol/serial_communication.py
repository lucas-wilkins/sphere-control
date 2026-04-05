import logging
import time

import serial

from serial.tools import list_ports

from firmware.lights.light_messages import LightMessageType
from firmware.motor.motor_messages import MotorMessageType

from test_sequences.axis_sequence import AxisSequence
from test_sequences.base_sequence import TestSequenceSeries
from test_sequences.chase_sequence import ChaseSequence
from test_sequences.rainbow import Rainbows

BAUD = 57600



class SerialControl:
    """ Main class for handling serial communication with all devices """
    def __init__(self,
                 stage_port ="dummy",
                 sphere_port ="dummy",
                 lights_port = "dummy"):

        self.lights_serial = DummyLightSerial() if lights_port == "dummy" else serial.Serial(lights_port, BAUD)
        self.stage_serial = DummyMotorSerial() if stage_port == "dummy" else serial.Serial(stage_port, BAUD)
        self.sphere_serial = DummyMotorSerial() if sphere_port == "dummy" else serial.Serial(sphere_port, BAUD)

        self.is_homed = False

    @staticmethod
    def auto_assign() -> "SerialControl":
        """ Automatically find the serial ports for devices """

        # Find all available serial ports
        ports = list_ports.comports()

        stage = "dummy"
        sphere = "dummy"
        lights = "dummy"

        for port in ports:
            print(port.name)

            if "USB" not in port.name and "COM" not in port.name and "ACM" not in port.name:
                print(f"{port.name} does not contain 'USB', 'ACM' or 'COM', skipping")
                continue

            try:
                with serial.Serial(port.device, BAUD, timeout=1) as ser:

                    time.sleep(2) # Wait for connection to initialise

                    ser.write(bytes([LightMessageType.IDENTIFY.value]))
                    data = ser.read(2)

                    if len(data) != 2:
                        print("Could not connect, timeout")
                        continue

                    response_type = int(data[0])

                    if response_type == LightMessageType.IDENTIFY.value:
                        print("System component")

                        component_type = int(data[1])

                        if component_type == LightMessageType.LIGHT_ID.value:
                            print("Lights")
                            lights = port.device

                        elif component_type == MotorMessageType.STAGE_MOTOR_ID.value:
                            print("Stage axis")
                            stage = port.device

                        elif component_type == MotorMessageType.SPHERE_MOTOR_ID.value:
                            print("Sphere axis")
                            sphere = port.device

                        else:
                            print("Unknown Component")

                    else:
                        print("Non-system component")



            except Exception as e:
                print(f"Failed to connect: {e}")

        return SerialControl(stage_port=stage, sphere_port=sphere, lights_port=lights)




class DummySerial:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.byte_queue: bytearray = bytearray()

    def write(self, msg: bytes):
        """ Stuff that happens on all dummy serial writes """
        # self.logger.info(msg)


    @property
    def in_waiting(self) -> int:
        return len(self.byte_queue)

    def read(self, n_bytes: int | None = None) -> bytes:
        data = bytes(self.byte_queue)
        if n_bytes is None:
            self.byte_queue = bytearray()
            return data
        else:

            if n_bytes <= len(data):
                to_return = data[:n_bytes]
                self.byte_queue = bytearray(data[n_bytes:])

            else:
                to_return = data
                self.byte_queue = bytearray()

            return to_return


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

        assert len(msg) > 0, "Don't send empty strings on serial"

        match MotorMessageType(int(msg[0])):
            case MotorMessageType.IDENTIFY:
                self._enqueue(bytes([MotorMessageType.IDENTIFY.value, MotorMessageType.STAGE_MOTOR_ID.value]))

            case MotorMessageType.QUERY_STATE:
                msg = (bytes([MotorMessageType.REPORT_STATE.value, MotorMessageType.IS_MOVING.value]) +
                      (123).to_bytes(4, byteorder='little', signed=True) +
                      (456).to_bytes(4, byteorder='little', signed=True))

                self._enqueue(msg)

            case MotorMessageType.GOTO_STEPS:
                self._enqueue(bytes([MotorMessageType.SERIAL_SUCCESS.value]))

            case MotorMessageType.INCREMENT_STEPS:
                self._enqueue(bytes([MotorMessageType.SERIAL_SUCCESS.value]))

            case _:
                self._enqueue(bytes([LightMessageType.UNKNOWN_REQUEST.value]))

if __name__ == "__main__":
    serial_coms = SerialControl.auto_assign()

