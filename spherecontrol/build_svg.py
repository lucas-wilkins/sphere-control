import math

import numpy as np

import matplotlib.pyplot as plt

from geometry.load_geometry import load_geometry
from lightdata import light_data

def project(data, x_factor):

    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    factor = np.sqrt(2/(1-x*x_factor))

    prj_x = y*factor
    prj_y = z*factor

    return np.array([prj_x, prj_y]).T

def graphics_layout(input_data: np.ndarray, x_factor=1) -> list[tuple[float, float, str]]:
    output = []

    prj = project(input_data, x_factor)

    for i, (a, b) in enumerate(zip(prj[:,0], prj[:,1])):
        output.append((a, b, str(i)))

    return output

def plot_graphics_layout(data: list[tuple[float, float, str]]):

    x = [datum[0] for datum in data]
    y = [datum[1] for datum in data]

    plt.plot(x, y)

    plt.scatter(x, y)

    for x, y, name in data:
        plt.text(x,y,name)

def format_poly_data(pts):
    strings = [f"{float(p[0])},{float(p[1])}" for p in pts]
    return " ".join(strings)

def build_svg(scale=500, point_radius=8, pad_fraction=0.6, font_size=8,
              shell_color="#444", wire_color="#555", ring_color="#555"):

    lines = [f'<svg width="{2*scale}" height="{scale}">']

    # The shapes of the two sphere halves
    top_shape = load_geometry("top")
    top_points = (scale/2)*(1 + pad_fraction*project(top_shape[:,(1,2,0)], 1) + np.array([2,0]).reshape(-1, 2))
    top_poly = format_poly_data(top_points)

    lines.append(f'  <polygon points="{top_poly}" fill="{shell_color}"/>')

    bottom_shape = load_geometry("bottom")
    bottom_points = (scale / 2) * (1 + pad_fraction * project(bottom_shape[:,(1,2,0)], -1))
    bottom_poly = format_poly_data(bottom_points)

    lines.append(f'  <polygon points="{bottom_poly}" fill="{shell_color}"/>')

    # Circles representing the equator
    equator_r = scale*pad_fraction/math.sqrt(2)
    lines.append(f'  <circle cx="{scale/2}" cy="{scale/2}" r="{equator_r}" '
                 f'stroke="{ring_color}" stroke-width="2" fill="none"/>')
    lines.append(f'  <circle cx="{3*scale/2}" cy="{scale/2}" r="{equator_r}" '
                 f'stroke="{ring_color}" stroke-width="2" fill="none"/>')

    # The path between the leds

    # The LEDs
    led_path = []
    led_circles = []
    for x,y,s in graphics_layout(light_data.top):

        cx = scale * (3+pad_fraction*x) / 2
        cy = scale * (1+pad_fraction*y) / 2

        led_path.append(f"{cx},{cy}")
        led_circles.append(f'  <circle id="led-top-{s}" cx="{cx}" cy="{cy}" r="{point_radius}" fill="#f0f"/>')
        led_circles.append(f'  <text id="led-top-{s}-text" x="{cx}" y="{cy}" '
                           f' text-anchor="middle" dominant-baseline="middle" fill="#000"'
                           f' font-size="{font_size}" font-family="Arial">{s}</text>')

    led_path = " ".join(led_path)
    lines.append(f'  <polyline points="{led_path}" fill="none" stroke="{wire_color}" stroke-width="3"/>')
    lines += led_circles

    led_path = []
    led_circles = []
    for x,y,s in graphics_layout(light_data.bottom, x_factor=-1):
        cx = scale * (1+pad_fraction*x) / 2
        cy = scale * (1+pad_fraction*y) / 2


        led_path.append(f"{cx},{cy}")
        led_circles.append(f'  <circle id="led-bottom-{s}" cx="{cx}" cy="{cy}" r="{point_radius}" fill="#f0f"/>')
        led_circles.append(f'  <text id="led-bottom-{s}-text" x="{cx}" y="{cy}" '
                           f' text-anchor="middle" dominant-baseline="middle" fill="#000"'
                           f' font-size="{font_size}" font-family="Arial">{s}</text>')

    led_path = " ".join(led_path)
    lines.append(f'  <polyline points="{led_path}" fill="none" stroke="{wire_color}" stroke-width="3"/>')
    lines += led_circles

    lines.append("</svg>")

    text = "\n".join(lines)

    with open("graphics/lights.svg", 'w') as file:
        file.write(text)

    return text

if __name__ == "__main__":

    build_svg()
    #
    # plt.figure("Top")
    # plot_graphics_layout(graphics_layout(light_data.top, 1))
    #
    # plt.figure("Bottom")
    # plot_graphics_layout(graphics_layout(light_data.bottom, -1))
    #
    # plt.show()