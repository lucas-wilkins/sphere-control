import numpy as np
from numpy._typing import ArrayLike

from lightdata import light_data
from test_sequences.base_sequence import FullSpecificationTestSequence


class AxisSequence(FullSpecificationTestSequence):

    def __init__(self, axis: ArrayLike=(1,0,0), color: ArrayLike=(1,1,1), total_time: float=5, width: float=0.2):
        self.axis = np.array(axis)

        self.led_positions = (self.led_xyz @ self.axis).reshape(-1, 1)
        self.color = np.array(color).reshape(1, 3)
        self.total_time = total_time
        self.width = width

    def length(self):
        return self.total_time

    def position(self, time):
        fraction = time / self.total_time
        return 3 * fraction - 1.5

    def window(self, positions):
        """ How choose the intensity of LEDs"""
        return np.exp((-0.5/self.width**2)*(positions**2))

    def light_colors(self, time) -> np.ndarray:
        intensities = self.window(self.led_positions - self.position(time)) * self.color
        return np.array(intensities*255, dtype=np.uint8)


if __name__ == "__main__":
    AxisSequence().serve()