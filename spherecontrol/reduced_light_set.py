""" List of lights that form subpatterns of the overall grid """
from collections import defaultdict

from scipy.spatial import ConvexHull

from led_positions import led_points_and_angles
from led_raw_to_string_mapping import mapping as led_mapping

def edge_mapping(points) -> tuple[dict[int, set[int]], set[tuple[int, int]]]:

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
    edge_list = []
    for a, b in edges:
        connection_map[a].append(b)
        connection_map[b].append(a)

        if a > b:
            edge_list.append((a, b))
        else:
            edge_list.append((b, a))

    connection_map = {key: set(value) for key, value in connection_map.items()}

    return connection_map, set(edge_list)

def _find_smaller_subdivision():

    # Make a map of which vertices are next to which

    points = led_points_and_angles[:, :3]
    connection_map, _ = edge_mapping(points)

    assert len(connection_map) == 162

    # Find the points and corresponding edges of the base icosahedron

    icos_inds = [key for key, value in connection_map.items() if len(value) == 5]

    assert len(icos_inds) == 12

    icos_points = points[icos_inds, :]
    _, icos_edges = edge_mapping(icos_points)

    assert len(icos_edges) == 30

    icos_edges = [(icos_inds[a], icos_inds[b]) for a, b in icos_edges]

    middles = []

    # find points which share neighbours with
    for a, b in icos_edges:
        a_neighbours = connection_map[a]
        b_neighbours = connection_map[b]

        for ind in connection_map:
            test_neighbours = connection_map[ind]
            if a_neighbours.intersection(test_neighbours) and b_neighbours.intersection(test_neighbours):
                #print(a, b, ind)
                middles.append(ind)

    both = icos_inds + middles
    rest = [i for i in range(points.shape[0]) if i not in both]

    return icos_inds, middles, rest

def plot_smaller_subdivision():
    import matplotlib.pyplot as plt

    points = led_points_and_angles[:, :3]
    icos_inds, middles, rest = _find_smaller_subdivision()

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    for inds, color in [
        (icos_inds, 'r'),
        (middles, 'b'),
        (rest, [0.8]*3)]:

        ax.scatter(points[inds, 0], points[inds, 1], points[inds, 2], color=color, s=150)

    plt.axis("equal")
    plt.show()

def icosahedron_indices():
    icos_inds, _, _ = _find_smaller_subdivision()

    return [led_mapping[ind] for ind in icos_inds if led_mapping[ind] is not None]

def smaller_subdivision_indices():
    icos_inds, middle, _ = _find_smaller_subdivision()

    return [led_mapping[ind] for ind in icos_inds + middle if led_mapping[ind] is not None]



if __name__ == "__main__":
    print("Available icosahedron indices:", len(icosahedron_indices()))
    print("Available subdivision indices:", len(smaller_subdivision_indices()))
    plot_smaller_subdivision()