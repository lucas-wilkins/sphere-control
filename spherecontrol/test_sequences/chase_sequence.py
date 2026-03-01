import numpy as np

from spherecontrol.test_sequences.base_sequence import SingleLightTestSequence

class ChaseSequence(SingleLightTestSequence):
    def __init__(self, speed):
        self.speed = speed

    def light_choice(self, time) -> int:
        return int(time*self.speed)

    def length(self):
        return 153.0/self.speed


if __name__ == "__main__":
    ChaseSequence().serve(speed=2, dt=0.05)


