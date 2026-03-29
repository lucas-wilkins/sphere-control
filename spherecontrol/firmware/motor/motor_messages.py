
""" Motor Messages

This is automatically generated from LightMessages.h, via create_python_message_id_enum.py

DO NOT EDIT MANUALLY
"""

from enum import Enum

class MotorMessageType(Enum):
    GET_POSITION = 10
    REPORT_POSITION = 11
    INCONSISTENT_STATE = 12
    GOTO = 20
    GOTO_STEPS = 21
    INCREMENT_STEPS = 22
    MOVING = 25
    MOVE_COMPLETE = 26
    SET_HOME = 30
    HOME_DONE = 31
    MANUAL_ON = 40
    MANUAL_OFF = 41
    UNKNOWN_REQUEST = 99
    IDENTIFY = 100
    SERIAL_SUCCESS = 200
    SERIAL_ERROR = 201
    STAGE_MOTOR_ID = 2
    SPHERE_MOTOR_ID = 3

