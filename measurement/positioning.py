from abc import abstractmethod, ABC
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

from geodesic import geodesic_angles_deg
from spherecontrol.configuration import config

class PositionPathing(ABC):
    def __init__(self, stage_angles_deg, sphere_angles_deg):
        self.stage_angles = stage_angles_deg
        self.sphere_angles = sphere_angles_deg

        low, high = config.sphere_limits_deg

        self.is_allowed = np.logical_and(low <= sphere_angles_deg, sphere_angles_deg <= high)

        self.allowed_stage_angles = self.stage_angles[self.is_allowed]
        self.allowed_sphere_angles = self.sphere_angles[self.is_allowed]

        self.disallowed_stage_angles = self.stage_angles[~self.is_allowed]
        self.disallowed_sphere_angles = self.sphere_angles[~self.is_allowed]

        self.apply_pathing()

    @abstractmethod
    def apply_pathing(self):
        """ Rearrange the allowed stage and sphere angles to the order which we want to visit them"""

    def plot(self):

        to_rad = np.pi / 180

        for stage_angle, sphere_angle, color, draw_line in [
            (self.allowed_stage_angles, self.allowed_sphere_angles, 'k', True),
            (self.disallowed_stage_angles, self.disallowed_sphere_angles, 'r', False)]:

            stage = stage_angle * to_rad
            sphere = sphere_angle * to_rad

            z = np.sin(sphere)
            r = np.cos(sphere)
            y = r * np.sin(stage)
            x = r * np.cos(stage)

            z_not_one = z != 1
            z_factor = np.sqrt(2 / (1-z[z_not_one]))

            x_prj = z_factor*x[z_not_one]
            y_prj = z_factor*y[z_not_one]

            plt.scatter(x_prj, y_prj, color=color)

            if draw_line:
                plt.plot(x_prj, y_prj, color=color)

                for i in range(len(sphere)):
                    plt.text(x_prj[i], y_prj[i], s=f"{i+1}")

            if np.sum(~z_not_one) > 0:
                plt.scatter([0], [2], color=color)

        circle_angles = np.linspace(0, 2*np.pi, 101)
        circle_x = np.cos(circle_angles)
        circle_y = np.sin(circle_angles)

        plt.plot(np.sqrt(2)*circle_x, np.sqrt(2)*circle_y, color='k', alpha=0.5)
        plt.plot(2*circle_x, 2*circle_y, color='k', alpha=0.5)

        plt.axis("equal")

def spiral_biased_argmin(z: np.ndarray, stage_angles_rad: np.ndarray, last_stage_angle_rad: float, tol=0.05):
    """ Basically argmin, but if two locations are close (the same within tolerance) in z, always pick the same direction"""
    smallest_ind = np.argmin(z)
    is_close = np.abs(z - z[smallest_ind]) < tol

    print("zs:", z)
    print("candidates, z:", z[is_close])
    print("candidates, angle:", stage_angles_rad[is_close])
    print()

    close_inds = np.arange(len(z), dtype=int)[is_close]

    diffs = stage_angles_rad[is_close] - last_stage_angle_rad

    diffs %= 2*np.pi # Wrap into offset in one direction

    least_rotation = np.argmin(diffs)

    return int(close_inds[least_rotation])


class SpiralPathing(PositionPathing):
    def apply_pathing(self):
        # Step 1, find the convex hull
        to_rad = np.pi / 180

        stage = self.allowed_stage_angles * to_rad
        sphere = self.allowed_sphere_angles * to_rad

        z = np.sin(sphere)
        r = np.cos(sphere)
        y = r * np.sin(stage)
        x = r * np.cos(stage)

        points = np.array([x,y,z]).T

        hull = ConvexHull(points)

        verts = [int(vert) for vert in hull.vertices]

        n_points = len(verts)

        # Need to map vertices
        vertex_point_mapping = {int(verts[i]): i for i in range(n_points)}

        faces = [[vertex_point_mapping[face[i]]
                  for i in range(3)]
                 for face in hull.simplices]

        edges = []
        for face in faces:
            edges.append((face[0], face[1]))
            edges.append((face[1], face[2]))
            edges.append((face[2], face[0]))

        connection_map = defaultdict(list)
        for a, b in edges:
            connection_map[a].append(b)
            connection_map[b].append(a)

        connection_map = {key: set(value) for key, value in connection_map.items()}

        # Search for the ordering ...

        visited = np.zeros((n_points,), dtype=bool)
        path = []

        ## Start point has the most negative z

        current = int(np.argmin(z))

        path.append(current)
        visited[current] = True

        # Run pathing
        while True:
            while True:
                connected = connection_map[current]
                possible = [i for i in connected if not visited[i]]

                if not possible:
                    break

                print("Point:", len(path))
                lowest_possible = spiral_biased_argmin(z[possible], stage[possible], stage[current])
                current = possible[lowest_possible]

                path.append(current)
                visited[current] = True

            if np.all(visited):
                break

            # We've gone through all the points that are connected
            # Find the next closest

            remaining_indices = np.array(verts)[~visited]
            remaining = points[remaining_indices, :]

            d_sq = np.sum((remaining - points[current, :]**2), axis=1)

            nearest = remaining_indices[np.argmin(d_sq)]

            current = int(nearest)
            visited[current] = True
            path.append(current)

        # Apply the ordering
        self.allowed_stage_angles = self.allowed_stage_angles[path]
        self.allowed_sphere_angles = self.allowed_sphere_angles[path]



if __name__ == "__main__":
    sta, sph = geodesic_angles_deg(1)
    path = SpiralPathing(sta, sph)

    path.plot()
    plt.show()