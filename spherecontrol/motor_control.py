import logging
import threading
import time
from typing import Callable

import serial

from firmware.motor.motor_messages import MotorMessageType
from serial_communication import SerialControl

class MotorControlPause:
    """ Does `with` statement that pauses motor position updates """
    def __init__(self, motor_control: "MotorControl"):
        self.motor_control = motor_control

    def __enter__(self):
        self.motor_control.position_update_stop.set()

    def __exit__(self, exc_type, exc_value, traceback):
        self.motor_control.schedule_position_updates(
            self.motor_control._position_update_callback)

class Empty:
    """ Can be used in `with`, does nothing"""
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass

class MotorControl:
    """ Interface for motor stuff """

    def __init__(self,
                 serial_object: serial.Serial,
                 motor_type: str,
                 steps_per_revolution,
                 encoder_positions_per_revolution):

        self.motor_id = f"Motor::{motor_type}"
        self.logger = logging.getLogger(self.motor_id)
        self.serial = serial_object

        self._position_update_stop = threading.Event()
        self._position_update_callback = None
        self._position_update_dt = 0.2

        self.steps_per_revolution = steps_per_revolution
        self.encoder_positions_per_revolution = encoder_positions_per_revolution

    def schedule_position_updates(self, callback: Callable[[bool, int, int], None]):
        """ Get position updates - runs the callback on the data obtained """

        def update_loop(stop_event, callback, dt):
            next_time = time.monotonic()

            while not stop_event.is_set():

                if callback is not None:
                    position = self.get_state()

                    if position is not None:
                        callback(*position)

                next_time += dt
                time.sleep(max(0, next_time - time.monotonic()))

        stop_event = threading.Event()
        threading.Thread(target=update_loop, args=(stop_event, callback, self._position_update_dt), daemon=True).start()

        self.position_update_stop = stop_event

    def paused(self):
        """ Pause position updates """
        if self._position_update_callback is None:
            return Empty()
        else:
            return MotorControlPause(self)

    def goto_steps(self, target: int):
        self.logger.info(f"Request position of {target} steps")

        msg = bytes([MotorMessageType.GOTO_STEPS.value]) + target.to_bytes(4, byteorder='little', signed=True)
        self.serial.write(msg)

        data = self.serial.read(1)
        response_type = int(data[0])

        if len(data) != 1:
            self.logger.error("Timeout")

        if response_type == MotorMessageType.SERIAL_SUCCESS.value:
            self.logger.info("OK")

        elif response_type == MotorMessageType.SERIAL_ERROR.value:
            self.logger.error("Serial error")

        else:
            self.logger.error("Unknown response")

    def move_to_encoder_position(self, target_encoder_position, max_attempts = 10, do_log=True):

        # Get the current position
        moving = True
        encoder_pos = 0
        while moving:
            moving, encoder_pos, _ = self.get_state()

        if do_log:
            self.logger.info(f"Starting encoder based move at {encoder_pos}")

        for i in range(max_attempts):

            # Get the number of steps needed to get to the desired motor position
            difference_encoder = target_encoder_position - encoder_pos
            difference_steps = int(difference_encoder * self.steps_per_revolution / self.encoder_positions_per_revolution)

            if do_log:
                self.logger.info(f"Moving {difference_steps} steps")

            # Move that number of steps
            self.increment_steps(difference_steps)

            # Get the current position
            moving = True
            encoder_pos = 0
            while moving:
                moving, encoder_pos, _ = self.get_state()

            if do_log:
                self.logger.info(f"New encoder position: {encoder_pos}")

            if encoder_pos == target_encoder_position:
                break

        else:
            self.logger.error(f"Failed to reach encoder position after {max_attempts} attempts")

    def increment_steps(self, delta: int, do_log=False):

        if do_log:
            self.logger.info(f"Request position increment of {delta} steps")

        msg = bytes([MotorMessageType.INCREMENT_STEPS.value]) + delta.to_bytes(4, byteorder='little', signed=True)
        self.serial.write(msg)

        data = self.serial.read(1)
        response_type = int(data[0])

        if len(data) != 1:
            self.logger.error("Timeout")

        if response_type == MotorMessageType.SERIAL_SUCCESS.value:
            self.logger.info("OK")

        elif response_type == MotorMessageType.SERIAL_ERROR.value:
            self.logger.error("Serial error")

        else:
            self.logger.error("Unknown response")

    def get_state(self) -> tuple[bool, int, int] | None:
        """ Get the current state: (moving, encoder, steps)"""

        self.serial.write(bytes([MotorMessageType.QUERY_STATE.value]))

        data = self.serial.read(1)

        if len(data) != 1:
            self.logger.error("Timeout")
            return None

        response_type = int(data[0])

        if response_type == MotorMessageType.REPORT_STATE.value:
            # All good

            data = self.serial.read(9)

            if len(data) != 9:
                self.logger.error("Timeout")
                return None

            if data[0] == MotorMessageType.IS_MOVING.value:
                moving = True
            elif data[0] == MotorMessageType.NOT_MOVING.value:
                moving = False
            else:
                self.logger.error("Bad move state")
                return None

            encoder_pos = int.from_bytes(data[1:5], byteorder='little', signed=True)
            step_pos = int.from_bytes(data[5:], byteorder='little', signed=True)

            return moving, encoder_pos, step_pos

        else:
            self._report_bad_response(data)
            return None


    def _report_bad_response(self, data: bytes):
        try:
            message_type = MotorMessageType(int(data[0]))
        except:
            message_type = data

        self.logger.error(f"Received incorrect response ({message_type})")

    def move(self, position_encoder):
        """ Move to the encoder position specified"""

    def move_steps(self, position_steps):
        """ Move to the step position specified """

    def set_limits(self, low, high):
        self.logger.info(f"Setting limits to [{low}, {high}]")

        if high <= low:
            raise ValueError(f"'low' ({low}) should be less than 'high' ({high})")

        msg = (bytes([MotorMessageType.SET_LIMITS.value]) +
               low.to_bytes(4, byteorder='little', signed=True) +
               high.to_bytes(4, byteorder='little', signed=True) )

        self.serial.write(msg)

        data = self.serial.read(1)
        response_type = int(data[0])

        if len(data) != 1:
            self.logger.error("Timeout")

        if response_type == MotorMessageType.SERIAL_SUCCESS.value:
            self.logger.info("OK")

        elif response_type == MotorMessageType.SERIAL_ERROR.value:
            self.logger.error(f"Failed to set limits to [{low}, {high}]")

        else:
            self.logger.error("Unknown response")

    def set_home(self):
        msg = bytes([MotorMessageType.SET_HOME.value])
        self.serial.write(msg)


if __name__ == "__main__":
    serial_comms = SerialControl.auto_assign()

    time.sleep(2)

    stage_motor = MotorControl(serial_comms.stage_serial, "Stage", 64000, 4096)

    # print(stage_motor.get_position())

    stage_motor.goto_steps(10000)

    for i in range(25):
        time.sleep(0.01)
        print(i, ":", stage_motor.get_state())

    stage_motor.goto_steps(0)

    for i in range(25):
        time.sleep(0.01)
        print(i, ":", stage_motor.get_state())
