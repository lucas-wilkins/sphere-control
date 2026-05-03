import numpy as np
from matplotlib import pyplot as plt

from led_positions import led_points_and_angles
from led_positions import point_plot
from position_input_tools import map_path, plot_path

ax = point_plot(show_numbers=False)

bottom_start = 158
bottom_up = 161
bottom_path = ("LU LU LU LU                  "
               "LD R  R  R  RU R             "
               "R  R  RU R  RU               "
               "RD L  L  LU LD LU L  LU L    "
               "L  L  L  LU LD LU L  LU L    "
               "RD R  R  RU RD RU RD RU R  R "
               "R  R  RD RU RD RU RD RU RU   "
               "RD L  L  LD LU LD LU LD LU L  L "
               "L  L  L  LD LU LD LU LD LU L  L")


top_start = 79
top_up = 0
top_path = ("RU LU RU LU LU LU          "
            "LU LU LU LD LD RD LD RD    "
            "R  RU L  RU U  UR R  R  RU "
            "R  RU R  RU R  R  D  RD LD "
            "L  LU U  LU L  L  LU L     "
            "L  L  L  LU L  L  D        "
            "RD U  RD U  RD D  RU       "
            "RU R  R  R  R              "
            "LD L  L  L  L              "
            "RD R  R  R  R  RU          "
            "RU RU RU RD D  L  L        ")

bottom_indices = map_path(bottom_path, bottom_start, bottom_up)
top_indices = map_path(top_path, top_start, top_up)
top_indices.reverse() # Top is backwards

plot_path(ax, bottom_indices)
plot_path(ax, top_indices)

plt.show()

bottom_data = led_points_and_angles[bottom_indices, :]
top_data = led_points_and_angles[top_indices, :]

np.save("geometry/bottom_data.npy", bottom_data)
np.save("geometry/top_data.npy", top_data)

# bottom_indices and top_indices are a mapping from led string index to the positional data,
#  we want mappings in the other direction too

all_indices = bottom_indices + top_indices
sequence_mapping = {ind: i for i, ind in enumerate(all_indices)}

for ind in set([i for i in range(162)]).difference(all_indices):
    sequence_mapping[ind] = None

import pickle
with open("geometry/index_map.pickle", 'wb') as file:
    pickle.dump(sequence_mapping, file)


