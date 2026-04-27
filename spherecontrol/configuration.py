import json
import os.path
from dataclasses import dataclass, asdict

_config_file = "config.json"

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

    @staticmethod
    def load():
        """ Load from file"""
        if os.path.exists(_config_file):
            with open(_config_file, 'r') as file:
                data = json.load(file)
                return Configuration(**data)
        else:
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



