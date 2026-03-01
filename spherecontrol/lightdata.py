from importlib import resources

import numpy as np


class LightData:
    def __init__(self):
        top_path = resources.files("spherecontrol.geometry") / "top_data.npy"
        bottom_path = resources.files("spherecontrol.geometry") / "bottom_data.npy"
        self.bottom: np.ndarray = np.load(bottom_path)
        self.top: np.ndarray = np.load(top_path)

        self.all = np.concatenate((self.bottom, self.top), axis=0)

light_data = LightData()