import threading
import time
from abc import abstractmethod, ABC
from dataclasses import dataclass
from threading import Event
from typing import Callable, Any

import numpy as np

from graphicsserver import GraphicsServer
from light_commands import full_specification, single_light
from lightdata import light_data


@dataclass
class LightState:
    top: np.ndarray
    bottom: np.ndarray

class TestSequence(ABC):
    """ Base class for test test_sequences """

    @abstractmethod
    def length(self) -> float:
        """ Length of the sequence """

    def light_command(self, time):
        """ Get the command for this time point"""
        return self._light_command(time % self.length())

    @abstractmethod
    def _light_command(self, time) -> bytes:
        """ The command that is to be sent to the controller """

    def run(self, callback: Callable[[bytes], Any], dt: float, speed: float = 1.0, on_stop: Callable[[], None] | None = None) -> threading.Event:

        sequence = self

        def update_loop(stop_event):
            next_time = time.monotonic()

            while not stop_event.is_set():
                callback(sequence.light_command(next_time*speed))
                next_time += dt
                time.sleep(max(0, next_time - time.monotonic()))

            if on_stop is not None:
                on_stop()

        stop_event = threading.Event()
        threading.Thread(target=update_loop, args=(stop_event,), daemon=True).start()

        return stop_event

    def serve(self, host: str="localhost", port: int=8080, dt: float=0.1, speed: float=1.0):
        server = GraphicsServer(host, port)
        self.run(server.light_control, dt, speed)
        server.run()

class SingleLightTestSequence(TestSequence):

    @abstractmethod
    def light_choice(self, time) -> int:
        """ Light at specified time"""

    def light_color(self, time) -> tuple[int, int, int] | None:
        return None

    def _light_command(self, time):
        return single_light(self.light_choice(time), self.light_color(time))

class FullSpecificationTestSequence(TestSequence):
    """ Light sequence where every led is specified"""

    led_xyz = light_data.all[:, :3]

    @abstractmethod
    def light_colors(self, time) -> np.ndarray:
        """ Colors of the top lights at a given time"""

    def _light_command(self, time):
        colors = self.light_colors(time)

        return full_specification(colors[:75, :], colors[75:, :])


class TestSequenceSeries(TestSequence):
    """ Sequence of test test_sequences """
    def __init__(self, *sequences: TestSequence):
        self.sequences = list(sequences)

        self.lengths = [sequence.length() for sequence in sequences]

        self.offsets = [0] + list(np.cumsum(self.lengths))

        self.total_length = sum(self.lengths)

    def length(self):
        return self.total_length

    def _light_command(self, time) -> bytes:
        for sequence, pre_offset, post_offset in zip(self.sequences, self.offsets, self.offsets[1:]):
            if pre_offset <= time < post_offset:
                return sequence.light_command(time - pre_offset)
        else:
            raise ValueError("Requested time outside of bounds")


class Black(FullSpecificationTestSequence):
    """ All off """
    def length(self):
        return 1.0

    def top_light_colors(self, time) -> np.ndarray:
        return np.zeros((78, 3), dtype=np.uint8)

    def bottom_light_colors(self, time) -> np.ndarray:
        return np.zeros((75, 3), dtype=np.uint8)


if __name__ == "__main__":
    black = Black()

    black.serve()