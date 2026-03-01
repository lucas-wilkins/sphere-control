from abc import ABC

import numpy as np

from test_sequences.base_sequence import FullSpecificationTestSequence


def hat_function(x: np.ndarray):
    r""" Function that is

      / x, x in [0,1],   part a
      | 2-x, x in [1, 2] part b
      \ 0, x in [2, 3]   part c

    """

    output = np.zeros_like(x)
    a = x < 1
    b = np.logical_and(x < 2, ~a)

    output[a] = x[a]
    output[b] = 2 - x[b]

    return output

def rainbow_colors(hue: np.ndarray):
    x = 3*hue.reshape(-1, 1)

    float_colors = np.concatenate((
        hat_function(x%3),
        hat_function((x+1)%3),
        hat_function((x+2)%3)), axis=1)

    return np.array(255*float_colors, dtype=np.uint8)

class Rainbows(FullSpecificationTestSequence):
    def __init__(self, period=10):
        self.period = period

    def length(self):
        return self.period

    def light_colors(self, time) -> np.ndarray:
        t = 2 * np.pi * time / self.length()

        a = 3*t
        b = 5*t
        c = 2*t

        axis = np.array([np.cos(a) * np.sin(b), np.sin(a) * np.sin(b), np.cos(b)])

        position = 0.5*(self.led_xyz @ axis)

        hue = position + (time / self.length())%1

        return rainbow_colors(hue)

if __name__ == "__main__":
    Rainbows().serve()