from test_sequences.axis_sequence import AxisSequence
from test_sequences.base_sequence import TestSequenceSeries

if __name__ == "__main__":
    sequencer = TestSequenceSeries(
                    AxisSequence(axis=(1,0,0), color=(1,0,0)),
                    AxisSequence(axis=(0,1,0), color=(0,1,0)),
                    AxisSequence(axis=(0,0,1), color=(0,0,1)))

    sequencer.serve(dt=0.05)
