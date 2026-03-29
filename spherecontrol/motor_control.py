import logging

import serial

from firmware.motor.motor_messages import MotorMessageType
from serial_communication import SerialControl


class MotorControl:

    def __init__(self, serial_object: serial.Serial, motor_type):
        self.logger = logging.getLogger(f"Motor::{motor_type}")
        self.serial = serial_object

    def goto_steps(self, target: int):
        msg = bytes([MotorMessageType.GOTO_STEPS.value]) + target.to_bytes(4, byteorder='little', signed=True)
        self.serial.write(msg)

        data = self.serial.read(1)
        response_type = int(data[0])

        if len(data) != 1:
            self.logger.error("Timeout")

        if response_type == MotorMessageType.SERIAL_SUCCESS.value:
            # OK
            pass

        elif response_type == MotorMessageType.SERIAL_ERROR.value:
            self.logger.error("Serial error")

        else:
            self.logger.error("Unknown response")

    def get_position(self) -> tuple[int, int] | None:
        self.serial.write(bytes([MotorMessageType.GET_POSITION.value]))

        data = self.serial.read(1)
        response_type = int(data[0])

        if len(data) != 1:
            self.logger.error("Timeout")
            return None

        if response_type == MotorMessageType.REPORT_POSITION.value:
            # All good
            data = self.serial.read(8)

            if len(data) != 8:
                self.logger.error("Timeout")
                return None

            value_1 = int.from_bytes(data[:4], byteorder='little', signed=True)
            value_2 = int.from_bytes(data[4:], byteorder='little', signed=True)

            return value_1, value_2

        else:
            self.logger.error(f"Received incorrect response ({data})")
            return None


    def increment_steps(self, steps):
        pass

    def move(self, position_encoder):
        """ Move to the encoder position specified"""

    def move_steps(self, position_steps):
        """ Move to the step position specified """

    def set_home(self):
        pass


if __name__ == "__main__":
    serial_comms = SerialControl.auto_assign()

    stage_motor = MotorControl(serial_comms.stage_serial, "Stage")

    print(stage_motor.get_position())
    stage_motor.goto_steps(10000)

    for i in range(1000):
        print(stage_motor.get_position())