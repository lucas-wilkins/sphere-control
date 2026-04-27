import logging
from nexus import Nexus

logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s, %(name)s: %(message)s"
    )

Nexus(True)