import numpy as np

from firmware.lights.light_messages import LightMessageType


def single_light(id: int, color: tuple[int,int,int] | None=None):
    """ Set a single light """

    if color is None:
        return bytes([LightMessageType.SINGLE_LIGHT.value, id])

    else:
        return bytes([LightMessageType.SINGLE_LIGHT_COLOR.value, id, color[0], color[1], color[2]])

def full_specification(bottom_lights: np.ndarray, top_lights: np.ndarray):
    """ Set all the lights """

    bottom_data = bottom_lights.tobytes()
    top_data = top_lights.tobytes()
    header = bytes([LightMessageType.FULL_LIGHT_SPEC.value])

    return header + bottom_data + top_data

def lights_off():
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