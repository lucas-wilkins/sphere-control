import time

import numpy as np
import serial

from light_messages import LightMessageType
from light_commands import single_light, lights_off, full_specification


if __name__ == "__main__":
    ser = serial.Serial("COM14", 57600, timeout=1)

    matrix = np.array(np.arange(459) % 256, dtype=np.uint8).reshape(153, 3)

    messages = [
        ("Identification request", bytes([LightMessageType.IDENTIFY.value])),
        ("Set single light", single_light(4)),
        ("Set single light (color)", single_light(5, (123,45,67))),
        ("Set colours with full control", full_specification(matrix[:75, :], matrix[75:, :])),
        ("Malformed single light", bytes([LightMessageType.SINGLE_LIGHT.value])),
        ("Set lights off", lights_off()),
        ("Bad message type", bytes([77])),
        ("Bad message type", bytes([78])),

    ]

    time.sleep(2)

    for description, msg in messages:
        print("\n")
        print("Sending message: ", description)

        ser.write(msg)
        ser.flush()

        time.sleep(0.02)

        if ser.in_waiting > 0:

            msg_value = ser.read(1)
            try:
                msg_type = LightMessageType(int.from_bytes(msg_value))
                print(msg_type)

                if msg_type == LightMessageType.IDENTIFY:
                    thing_id = ser.read(1)

                    print(f"Identified as {thing_id}")

            except ValueError:
                print(f"Unknown message {int.from_bytes(msg_value)}")

            #bytes_read = ser.read(ser.in_waiting)
            #print(bytes_read)



        time.sleep(0.1)

