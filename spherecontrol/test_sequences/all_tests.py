from test_sequences.axis_sequence import AxisSequence
from test_sequences.base_sequence import TestSequenceSeries
from test_sequences.chase_sequence import ChaseSequence
from test_sequences.rainbow import Rainbows

if __name__ == "__main__":
    sequencer = TestSequenceSeries(
                    ChaseSequence(10),
                    AxisSequence(axis=(1,0,0), color=(1,0,0)),
                    AxisSequence(axis=(0,1,0), color=(0,1,0)),
                    AxisSequence(axis=(0,0,1), color=(0,0,1)),
                    Rainbows())

    sequencer.serve(dt=0.05)
