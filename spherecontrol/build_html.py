import importlib

from build_svg import build_svg


def build_html():
    svg_data = build_svg()

    template = importlib.resources.read_text("spherecontrol.html", "main_template.html")

    replaced = template.replace("<!-- Inject SVG Here -->", svg_data)

    with open("html/main.html", 'w') as file:
        file.write(replaced)

if __name__ == "__main__":
    build_html()


