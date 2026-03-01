import numpy as np

from spherecontrol.test_sequences.base_sequence import FullSpecificationTestSequence


class RandomSequence(FullSpecificationTestSequence):
    def top_light_colors(self, time) -> np.ndarray:
        return np.random.randint(255, size=(78,3), dtype=np.uint8)

    def bottom_light_colors(self, time) -> np.ndarray:
        return np.random.randint(255, size=(75, 3), dtype=np.uint8)

    def length(self):
        return 1


if __name__ == "__main__":
    RandomSequence().serve()
