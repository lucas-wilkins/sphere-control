
""" Motor Messages

This is automatically generated from LightMessages.h, via create_python_message_id_enum.py

DO NOT EDIT MANUALLY
"""

from enum import Enum

class MotorMessageType(Enum):
    GET_POSITION = 10
    REPORT_POSITION = 11
    INCONSISTENT_STATE = 12
    MOVE = 20
    MOVE_STEPS = 21
    MOVING = 25
    MOVE_COMPLETE = 26
    SET_HOME = 30
    HOME_DONE = 31
    MANUAL_ON = 40
    MANUAL_OFF = 41
    UNKNOWN_REQUEST = 99
    IDENTIFY = 100

