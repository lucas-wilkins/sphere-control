import numpy as np

def normalize(v):
    return v / np.linalg.norm(v)

def subdivide(v1, v2, v3, depth):
    """Recursively subdivide triangle into smaller triangles."""
    if depth == 0:
        return [v1, v2, v3]

    # midpoints
    v12 = normalize((v1 + v2) / 2)
    v23 = normalize((v2 + v3) / 2)
    v31 = normalize((v3 + v1) / 2)

    # Subdivide further
    return (
        subdivide(v1,  v12, v31, depth - 1) +
        subdivide(v12, v2,  v23, depth - 1) +
        subdivide(v31, v23, v3,  depth - 1) +
        subdivide(v12, v23, v31, depth - 1)
    )

def geodesic_sphere(subdivisions=1, radius=1.0):
    """Return unique vertices of a geodesic sphere."""
    t = (1.0 + np.sqrt(5.0)) / 2.0

    # Create icosahedron vertices
    verts = np.array([
        [-1,  t,  0], [1,  t,  0], [-1, -t, 0], [1, -t, 0],
        [0, -1,  t], [0, 1,  t], [0, -1, -t], [0, 1, -t],
        [t,  0, -1], [t,  0, 1], [-t, 0, -1], [-t, 0, 1]
    ], dtype=float)

    verts = np.array([normalize(v) for v in verts])

    # Faces of an icosahedron (20 triangles)
    faces = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7,10], [0,10,11],
        [1, 5, 9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ]

    sphere_vertices = []

    for f in faces:
        v1, v2, v3 = verts[f[0]], verts[f[1]], verts[f[2]]
        sphere_vertices.extend(subdivide(v1, v2, v3, subdivisions))

    # Remove duplicates
    sphere_vertices = np.array(sphere_vertices)
    sphere_vertices = np.unique(np.round(sphere_vertices, 6), axis=0)

    return sphere_vertices * radius

def geodesic_angles_deg(n_subdivisions: int):
    points = geodesic_sphere(n_subdivisions)

    x, y, z = points[:, 0], points[:, 1], points[:, 2]

    r = np.sqrt(x**2 + y**2)

    to_deg = 180 / np.pi
    stage_angle = np.atan2(y, x) * to_deg
    sphere_angle = np.atan2(z, r) * to_deg

    return stage_angle, sphere_angle






if __name__ == "__main__":
    points = geodesic_sphere(2)

    print(points)

    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(points[:, 0], points[:, 1], points[:, 2])

    plt.show()