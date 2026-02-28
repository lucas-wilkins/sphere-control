import numpy as np

import matplotlib.pyplot as plt

from lightdata import light_data

def graphics_layout(input_data: np.ndarray, x_factor=1) -> list[tuple[float, float, str]]:
    output = []

    x = input_data[:, 0]
    y = input_data[:, 1]
    z = input_data[:, 2]

    factor = np.sqrt(2/(1-x*x_factor))

    prj_x = y*factor
    prj_y = z*factor

    for i, (a, b) in enumerate(zip(prj_x, prj_y)):
        output.append((a, b, str(i)))

    return output

def plot_graphics_layout(data: list[tuple[float, float, str]]):

    x = [datum[0] for datum in data]
    y = [datum[1] for datum in data]

    plt.plot(x, y)

    plt.scatter(x, y)

    for x, y, name in data:
        plt.text(x,y,name)



def build_svg(scale=100, point_size=10):
    with open("lights.svg", 'w') as file:
        file.write("<svg>\n")

        file.write("</svg>\n")

if __name__ == "__main__":

    plt.figure("Top")
    plot_graphics_layout(graphics_layout(light_data.top, 1))

    plt.figure("Bottom")
    plot_graphics_layout(graphics_layout(light_data.bottom, -1))

    plt.show()