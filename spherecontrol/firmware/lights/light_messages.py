
""" Light Messages

This is automatically generated from LightMessages.h, via create_python_message_id_enum.py

DO NOT EDIT MANUALLY
"""

from enum import Enum

class LightMessageType(Enum):
    SINGLE_LIGHT = 1
    SINGLE_LIGHT_COLOR = 2
    FULL_LIGHT_SPEC = 3
    ALL_OFF = 4
    UNKNOWN_REQUEST = 99
    IDENTIFY = 100
    SERIAL_SUCCESS = 200
    SERIAL_ERROR = 201
    LIGHT_ID = 1

