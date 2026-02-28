from collections import defaultdict

import numpy as np

import matplotlib.pyplot as plt

from scipy.spatial import ConvexHull

from positions import led_points_and_angles, type_groups, point_plot, led_xyz


def normalise(v):
    return v / np.sqrt(np.sum(v**2))

def local_frame(point: np.ndarray, up: np.ndarray):
    """ Make cartesian coordinates at a given point

    z comes out of plane, in local frame it is the point (because its a sphere)
    y is up aligned
    x is other
    """

    z = -normalise(point)
    up = normalise(up)

    y = normalise(up - z * np.dot(z, up))
    x = np.cross(z, y)

    return np.array([x,y], dtype=float)

directions = {key: np.array(value, dtype=float) for key, value in {
    "L": [-1, 0],
    "UL": [-1, 1],
    "U": [0, 1],
    "UR": [1, 1],
    "R": [1, 0],
    "DR": [1, -1],
    "D": [0, -1],
    "DL": [-1, -1]}.items()}

for direction in [key for key in directions.keys()]:
    if len(direction) > 1:
        directions[direction[::-1]] = directions[direction]

angles = {index: float(np.arctan2(v[1], v[0])) for index, v in directions.items()}

def neighbour_mapping():
    hull = ConvexHull(led_xyz)

    verts = hull.vertices

    neighbours = defaultdict(list)

    for simplex in hull.simplices:

        a,b,c = [int(x) for x in verts[simplex]]

        neighbours[a].append(b)
        neighbours[a].append(c)
        neighbours[b].append(a)
        neighbours[b].append(c)
        neighbours[c].append(a)
        neighbours[c].append(b)

    refined = {key: list(set(neighbours[key])) for key in neighbours}

    return refined

neighbours = neighbour_mapping()

def map_path(path: str, start: int, up: int):

    tokens = [token for token in path.split(" ") if len(token) > 0]

    up = led_xyz[up, :]

    current_index = start
    indices = [start]

    for token in tokens:
        current_position = led_xyz[current_index, :]

        frame = local_frame(current_position, up)
        #
        # ax = point_plot()
        # for label, direction in directions.items():
        #     v = direction @ frame
        #     p = current_position + v
        #     ax.plot([current_position[0], p[0]],
        #             [current_position[1], p[1]],
        #             [current_position[2], p[2]])
        #     ax.text(*p, s=label)
        #
        # plt.show()

        neighbour_indices = neighbours[current_index]
        neighbour_points_in_plane = (led_xyz[neighbour_indices, :] - current_position) @ frame.T
        neighbour_angles = np.arctan2(neighbour_points_in_plane[:, 1], neighbour_points_in_plane[:, 0])

        angle = angles[token.upper()]
        angle_deltas = (neighbour_angles - angle).reshape(-1, 1) + np.pi*np.array([-2, 0, 2]).reshape(1, -1)
        angle_distance = np.min(np.abs(angle_deltas), axis=1)

        current_index = neighbour_indices[np.argmin(angle_distance)]
        indices.append(current_index)

    return indices

def plot_path(ax, indices, color='k'):

    path_points = led_xyz[indices, :]
    ax.plot(path_points[:, 0], path_points[:, 1], path_points[:, 2])
    ax.axis("equal")
