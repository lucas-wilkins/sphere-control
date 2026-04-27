
import numpy as np

from spherecontrol.firmware.lights.light_messages import LightMessageType
from spherecontrol.lightdata import light_data

class LightCommand:
    def __init__(self,
                 command_type: LightMessageType,
                 light_index: int | None,
                 light_color: tuple[int, int, int] | None,
                 light_state_pair: tuple[np.ndarray, np.ndarray],
                 serial_command: bytes):

        self._command_type = command_type
        self._light_index = light_index
        self._light_color = (255, 255, 255) if light_color is None else light_color
        self._light_position_data = None if light_index is None else light_data.all[light_index, :]
        self._light_state_pair = light_state_pair
        self._light_state = np.concatenate(light_state_pair, axis=0)
        self._serial_command = serial_command

    @property
    def command_type(self) -> LightMessageType:
        """ What kind of command is this """
        return self._command_type

    @property
    def light_index(self) -> int | None:
        """ If it is a single light command, which light"""
        return self._light_index

    @property
    def light_position_data(self) -> np.ndarray | None:
        """ If it is a single light command, where is the light in space """
        return self._light_position_data

    @property
    def light_color(self) -> tuple[int, int, int] | None:
        return self._light_color

    @property
    def light_state_pair(self) -> tuple[np.ndarray, np.ndarray]:
        """ Full data on the light state, in top and bottom halves"""
        return self._light_state_pair

    def light_state(self) -> np.ndarray:
        """ Full data on the light state """
        return self._light_state

    @property
    def serial_command(self) -> bytes:
        """ Data to be sent over serial """
        return self._serial_command

    def info_string(self) -> str:
        pass

class SingleLight(LightCommand):
    def __init__(self, id: int, color: tuple[int, int, int] | None = None):

        command = single_light(id, color)
        data_pair = decode_light_command(command)

        super().__init__(
            command_type=LightMessageType.SINGLE_LIGHT if color is None else LightMessageType.SINGLE_LIGHT_COLOR,
            light_index=id,
            light_color=color,
            light_state_pair=data_pair,
            serial_command=command)


class GeneralLights(LightCommand):
    def __init__(self, bottom_lights_or_all_lights: np.ndarray, top_lights: np.ndarray | None = None):

        if top_lights is None:
            bottom_lights = bottom_lights_or_all_lights[:75, :]
            top_lights = bottom_lights_or_all_lights[75:, :]
        else:
            bottom_lights = bottom_lights_or_all_lights

        command = full_specification(bottom_lights, top_lights)

        super().__init__(
            command_type=LightMessageType.FULL_LIGHT_SPEC,
            light_index=None,
            light_color=None,
            light_state_pair=(bottom_lights, top_lights),
            serial_command=command)

class LightsOff(LightCommand):
    def __init__(self):
        bottom_lights = np.zeros((75, 3), dtype=np.uint8)
        top_lights = np.zeros((78, 3), dtype=np.uint8)

        super().__init__(
            command_type=LightMessageType.ALL_OFF,
            light_index=None,
            light_color=None,
            light_state_pair=(bottom_lights, top_lights),
            serial_command=lights_off())


def single_light(id: int, color: tuple[int,int,int] | None=None) -> bytes:
    """ Set a single light """

    if color is None:
        return bytes([LightMessageType.SINGLE_LIGHT.value, id])

    else:
        return bytes([LightMessageType.SINGLE_LIGHT_COLOR.value, id, color[0], color[1], color[2]])

def full_specification(bottom_lights: np.ndarray, top_lights: np.ndarray) -> bytes:
    """ Set all the lights """

    bottom_data = bottom_lights.tobytes()
    top_data = top_lights.tobytes()
    header = bytes([LightMessageType.FULL_LIGHT_SPEC.value])

    return header + bottom_data + top_data

def lights_off() -> bytes:
    return bytes([LightMessageType.ALL_OFF.value])

def decode_light_command(message: bytes, output=None) -> tuple[np.ndarray, np.ndarray]:
    """ Decode on of these messages """
    header = LightMessageType(int(message[0]))

    match header:
        case LightMessageType.SINGLE_LIGHT:

            if len(message) != 2:
                raise ValueError("Expected message type 1 to be two bytes long")

            output = np.zeros((153, 3), dtype=np.uint8)
            output[int(message[1]), :] = 255

        case LightMessageType.SINGLE_LIGHT_COLOR:
            if len(message) != 5:
                raise ValueError("Expected message type 2 to be five bytes long")

            output = np.zeros((153, 3), dtype=np.uint8)
            light = int(message[1])
            output[light, 0] = int(message[2])
            output[light, 1] = int(message[3])
            output[light, 2] = int(message[4])

        case LightMessageType.FULL_LIGHT_SPEC:
            if len(message) != 460: # 1 + (153 x 3) = 460
                raise ValueError("Expected message of type 3 to be 460 bytes long")

            output = np.frombuffer(message[1:], dtype=np.uint8).reshape((153, 3))


        case LightMessageType.ALL_OFF:

            output = np.zeros((153, 3), dtype=np.uint8)

        case _:
            raise ValueError(f"Unknown message type: {header}")

    return output[:75, :], output[75:, :]