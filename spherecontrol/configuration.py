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



