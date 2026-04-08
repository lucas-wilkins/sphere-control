
""" Motor Messages

This is automatically generated from LightMessages.h, via create_python_message_id_enum.py

DO NOT EDIT MANUALLY
"""

from enum import Enum

class MotorMessageType(Enum):
    QUERY_STATE = 10
    REPORT_STATE = 11
    GOTO = 20
    GOTO_STEPS = 21
    INCREMENT_STEPS = 22
    IS_MOVING = 25
    NOT_MOVING = 26
    SET_HOME = 30
    HOME_DONE = 31
    SET_LIMITS = 35
    QUERY_LIMITS = 36
    MANUAL_ON = 40
    MANUAL_OFF = 41
    UNKNOWN_REQUEST = 99
    IDENTIFY = 100
    SERIAL_SUCCESS = 200
    SERIAL_ERROR = 201
    STAGE_MOTOR_ID = 2
    SPHERE_MOTOR_ID = 3

