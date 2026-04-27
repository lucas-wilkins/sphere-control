import pytest

from spherecontrol.control_server import ControlCommand
from spherecontrol.light_commands import SingleLight

@pytest.mark.parametrize("stage", [None, 1000])
@pytest.mark.parametrize("sphere", [None, -56565])
@pytest.mark.parametrize("message", [None, SingleLight(40, (4,56,65)).serial_command])
@pytest.mark.parametrize("wait", [True, False])
def test_control_command_encoding(stage, sphere, message, wait):
    cmd = ControlCommand(stage, sphere, message, wait)

    assert cmd == ControlCommand.from_bytes(cmd.to_bytes())

