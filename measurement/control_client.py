from dataclasses import dataclass

@dataclass
class ControlServerConfig:
    address: str = "127.0.0.1"
    port: int = 5555

class ControlClient:
    pass