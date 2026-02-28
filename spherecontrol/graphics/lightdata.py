import numpy as np


class LightData:
    def __init__(self):
        self.bottom: np.ndarray = np.load("../bottom_data.npy")
        self.top: np.ndarray = np.load("../top_data.npy")

light_data = LightData()