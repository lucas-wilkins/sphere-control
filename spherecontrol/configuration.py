import json
import logging
import os.path
from dataclasses import dataclass, asdict
from importlib import resources

_config_file = "config.json"
logger = logging.getLogger("Config")

@dataclass
class Configuration:
    """ Configuration for the system """

    sphere_axis_low: int = -64000
    sphere_axis_high: int = 64000
    sphere_axis_home_position: int = 2048
    stage_axis_home_position: int = 2048
    control_server_port: int = 5555
    stage_steps_per_revolution: int = 64000
    sphere_steps_per_revolution: int = 64000
    stage_encoder_positions_per_revolution: int = 4096
    sphere_encoder_positions_per_revolution: int = 4096
    homing_n_steps_during_search: int = 1
    homing_search_radius_steps: int = 30
    sphere_home_angle_deg: float = 0.0
    stage_home_angle_deg: float = 0.0

    @property
    def sphere_steps_per_encoder_position(self):
        return self.sphere_steps_per_revolution / self.sphere_encoder_positions_per_revolution

    @property
    def stage_steps_per_encoder_position(self):
        return self.stage_steps_per_revolution / self.stage_encoder_positions_per_revolution

    @property
    def sphere_limits_deg(self):
        """ Get the limits in degrees """
        to_deg = 360.0 / self.sphere_steps_per_revolution
        low = self.sphere_axis_low * to_deg + self.sphere_home_angle_deg
        high = self.sphere_axis_high * to_deg + self.sphere_home_angle_deg

        return low, high

    @staticmethod
    def load():
        """ Load from file"""
        if os.path.exists(_config_file):
            with open(_config_file, 'r') as file:
                data = json.load(file)
                return Configuration(**data)
        else:

            logger.warning("Failed to find config file, trying resources...")

            try:
                string_data = resources.read_text("spherecontrol", "config.json")
                data = json.loads(string_data)
                return Configuration(**data)

            except:
                logger.warning("Resources failed, using default config...")
                return Configuration()


    def save(self):
        """ Save to file"""
        data = asdict(self)
        with open(_config_file, 'w') as file:
            json.dump(data, file, indent=2)

config = Configuration.load()

if __name__ == "__main__":
    print(config)
    config.save()



