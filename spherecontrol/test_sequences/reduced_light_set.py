import numpy as np

from spherecontrol.test_sequences.base_sequence import FullSpecificationTestSequence, SingleLightTestSequence, TestSequenceSeries

from spherecontrol.reduced_light_set import icosahedron_indices, smaller_subdivision_indices

_smaller_subdivision_inds = smaller_subdivision_indices()
_icos_inds = icosahedron_indices()

class ReducedLightSequence(SingleLightTestSequence):
    def __init__(self, speed=2.0):
        self.speed = speed

    def light_choice(self, time) -> int:
        return _smaller_subdivision_inds[int(time * self.speed)]

    def length(self):
        return len(_smaller_subdivision_inds) / self.speed

class AllReducedLights(FullSpecificationTestSequence):
    def __init__(self):

        self.state = np.zeros((153, 3), dtype=np.uint8)
        self.state[_smaller_subdivision_inds, :] = 255

    def length(self):
        return 2

    def light_colors(self, time) -> np.ndarray:
        return self.state

full_reduced_lights = TestSequenceSeries(ReducedLightSequence(), AllReducedLights())

if __name__ == "__main__":
    # full_reduced_lights.serve()
    AllReducedLights().serve()