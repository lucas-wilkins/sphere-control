import pickle
from importlib import resources

with resources.open_binary("spherecontrol.geometry", "index_map.pickle") as file:
    mapping = pickle.load(file)

