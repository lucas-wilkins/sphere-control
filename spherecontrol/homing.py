from dataclasses import dataclass
from typing import Callable

import numpy as np

from simulations.motor_model import MotorModel


def gather_home_data(move_size: int,
                     search_radius_steps: int,
                     move_and_read_callback: Callable[[int], int],
                     n_sweeps: int = 5):
    """ Get the data needed for homing """

    forward_data = []
    backward_data = []

    n_moves = search_radius_steps // move_size

    position = 0
    for _ in range(n_moves):
        move_and_read_callback(-move_size)
        position -= move_size

    for sweep in range(n_sweeps):

        for move_direction, store_location in [(1, forward_data), (-1, backward_data)]:

            sweep_positions = []
            sweep_readings = []

            for _ in range(2*n_moves):

                move = move_direction * move_size

                reading = move_and_read_callback(move)
                position += move

                sweep_positions.append(position)
                sweep_readings.append(reading)

            store_location.append((sweep_positions, sweep_readings))

    for _ in range(n_moves):
        move_and_read_callback(move_size)

    return forward_data, backward_data


@dataclass
class HomeIntervals:
    forward: tuple[float, float]
    backward: tuple[float, float]

    @property
    def centre(self) -> float:
        return 0.25*(self.forward[0] + self.forward[1] + self.backward[0] + self.backward[1])

    @property
    def forward_centre(self) -> float:
        return 0.5 * (self.forward[0] + self.forward[1])

    @property
    def backward_centre(self) -> float:
        return 0.25 * (self.backward[0] + self.backward[1])


def find_edges(positions: list[int],
               encoder: list[int],
               target_value: int,
               encoder_range: int,
               reverse: bool=False):

    # Find edges of interval

    positions = np.array(positions, dtype=int)
    encoder = np.array(encoder, dtype=int)

    diff_positions = 0.5*(positions[:-1] + positions[1:])

    below = encoder == ((target_value - 1) % encoder_range)
    equal = encoder == target_value
    above = encoder == ((target_value + 1) % encoder_range)

    if reverse:

        diffs_below = np.logical_and(equal[:-1], below[1:])
        diffs_above = np.logical_and(equal[1:], above[:-1])

        diffs_below = diffs_below[::-1]
        diffs_above = diffs_above[::-1]
        diff_positions = diff_positions[::-1]

    else:
        diffs_below = np.logical_and(equal[1:], below[:-1])
        diffs_above = np.logical_and(equal[:-1], above[1:])

    below_index_list = np.where(diffs_below)[0]
    below_position = float(diff_positions[below_index_list[0]]) if below_index_list.size > 0 else None

    above_index_list = np.where(diffs_above)[0]
    above_position = float(diff_positions[above_index_list[0]]) if above_index_list.size > 0 else None

    return below_position, above_position

def edge_pairs(forward_data: list[tuple[list[int], list[int]]],
               backward_data: list[tuple[list[int], list[int]]],
               target_value: int, encoder_range: int) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:

    """ Get list of edges between encoder steps """

    forward_edges = [find_edges(positions, encoder, target_value, encoder_range, False)
                     for positions, encoder in forward_data]

    forward_edges = [(a, b) for a, b in forward_edges if a is not None and b is not None]


    backward_edges = [find_edges(positions, encoder, target_value, encoder_range, True)
                     for positions, encoder in backward_data]

    backward_edges = [(a, b) for a, b in backward_edges if a is not None and b is not None]

    return forward_edges, backward_edges

def process_homing_data(forward_data: list[tuple[list[int], list[int]]],
                        backward_data: list[tuple[list[int], list[int]]],
                        target_value: int, encoder_range: int) -> HomeIntervals:

    forward_edges, backward_edges = edge_pairs(forward_data, backward_data, target_value, encoder_range)

    if len(forward_edges) == 0 or len(backward_edges) == 0:
        raise Exception("Failed to home, no data")

    forward_low = [x for x, _ in forward_edges]
    forward_high = [x for _, x in forward_edges]

    backward_low = [x for x, _ in backward_edges]
    backward_high = [x for _, x in backward_edges]



    return HomeIntervals(
        forward = (float(np.mean(forward_low)), float(np.mean(forward_high))),
        backward = (float(np.mean(backward_low)), float(np.mean(backward_high)))
    )

def home(target_value: int,
         move_size: int,
         search_radius_steps: int,
         move_to_encoder_callback: Callable[[int], None],
         move_and_read_callback: Callable[[int], int],
         n_sweeps: int = 5,
         encoder_range: int = 4096):

    """ Main homing method

    The important thing here is that we home to *repeatable* position
    """

    # Move to encoder position which we want to home to
    move_to_encoder_callback(target_value)

    # Gather data and estimate intervals
    forward, backward = gather_home_data(move_size, search_radius_steps, move_and_read_callback, n_sweeps=n_sweeps)
    intervals =  process_homing_data(forward, backward, target_value, encoder_range=encoder_range)

    # Move the right amount, go backwards a bit, then for forwards towards estimated for that backlash position
    move_and_read_callback(-2*search_radius_steps)
    change = int(intervals.forward_centre) + 2*search_radius_steps
    move_and_read_callback(change)


if __name__ == "__main__":
    motor = MotorModel()

    home_target = 1000

    #
    # Plotting to check it works
    #

    motor.move_to_encoder_position(home_target)

    def move_and_read(n_steps):
        motor.move_steps(n_steps)
        return motor.get_encoded_position()

    forward, backward = gather_home_data(1, 22, move_and_read)

    forward_pairs, backward_pairs = edge_pairs(forward, backward, home_target, 4096)

    home_intervals = process_homing_data(forward, backward, home_target, 4096)

    import matplotlib.pyplot as plt

    for data in [forward, backward]:
        for positions, readings in data:
            plt.plot(positions, readings)

    for pair_data in [forward_pairs, backward_pairs]:
        for pair in pair_data:
            plt.scatter(pair, [home_target, home_target])

    for bounds in [home_intervals.forward, home_intervals.backward]:
        for pos in bounds:
            plt.plot([pos, pos], [home_target-2, home_target+2], color='k')

    #
    # Run full homing thing (might give slightly different results because of randomness in model)
    #

    home(1000, 1, 22, motor.move_to_encoder_position, move_and_read)

    print(motor.get_encoded_position())


    # Show plot

    plt.show()

