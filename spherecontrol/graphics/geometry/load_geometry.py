import importlib.resources
from collections import defaultdict

import numpy as np


def load_geometry(name, scale=135):

    vertices = []
    lines = defaultdict(list)

    for line in importlib.resources.read_text("spherecontrol.graphics.geometry", name+".obj").split("\n"):

        try:
            first_char = line[0]
        except IndexError:
            first_char = ""



        match first_char:
            case "v":
                parts = line.split(" ")
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            case "l":
                parts = line.split(" ")
                a, b = int(parts[1]), int(parts[2])
                lines[a].append(b)
                lines[b].append(a)
            case "f":
                print("Warning, geometry contains faces, should not do")
            case _:
                pass # print("Skipping:", line)


    # Clean up danglies
    lines = {key: value for key, value in lines.items()}
    while True:
        remove = []
        for i in lines.keys():
            if len(lines[i]) < 2:
                remove.append(i)

        if len(remove) == 0:
            break

        for to_remove in remove:
            print("Removing dangling line", lines[to_remove])

            del lines[to_remove]

            for i in lines.keys():
                if to_remove in lines[i]:
                    lines[i].remove(to_remove)



    # Search for a continuous line
    visited = np.zeros((len(vertices)+1,))


    vertex = 1

    ordered = [vertex]
    live = True
    while live:
        visited[vertex] = True

        live = False
        for next in lines[vertex]:
            if not visited[next]:
                vertex = next
                live = True
                break

        ordered.append(vertex)

    if 1 in lines[vertex]:
        print("Successful closed loop")
    else:
        print("Loop not closed, ended on", vertex, "with connections", lines[vertex])



    # return scaled to [-1, 1]
    return np.array([vertices[i-1] for i in ordered], dtype=float) / scale

if __name__ == "__main__":
    bottom_data = load_geometry("bottom")
    top_data = load_geometry("top")

    import matplotlib.pyplot as plt
    ax = plt.figure().add_subplot(projection='3d')
    ax.plot(bottom_data[:, 0], bottom_data[:, 1], bottom_data[:,2])
    ax.plot(top_data[:, 0], top_data[:, 1], top_data[:,2])
    plt.axis("equal")
    plt.show()