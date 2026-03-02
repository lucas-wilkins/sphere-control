from importlib import resources

from build_svg import build_svg


def build_html():
    led_svg_data = build_svg()
    orientation_svg_data = resources.read_text("spherecontrol.graphics", "orientation.svg")

    template = resources.read_text("spherecontrol.html", "main_template.html")



    replaced = template.replace("<!-- Inject SVGs Here -->", led_svg_data + orientation_svg_data)

    with open("html/main.html", 'w') as file:
        file.write(replaced)

if __name__ == "__main__":
    build_html()


