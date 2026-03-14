import importlib
import threading
import json
import logging


import numpy as np
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from spherecontrol.light_commands import decode_light_command
from spherecontrol.lightdata import light_data

class MotorPosition:
    def __init__(self, commanded: float, actual: float):
        self.commanded = commanded
        self.actual = actual


class GraphicsServer:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port


        self.top_lights = np.zeros((light_data.top.shape[0], 3), dtype=np.uint8)
        self.bottom_lights = np.zeros((light_data.bottom.shape[0], 3), dtype=np.uint8)
        self.stage_position = MotorPosition(0.0, 0.0)
        self.sphere_position = MotorPosition(90.0, 90.0)

        self._lock = threading.Lock()

        self._server = ThreadingHTTPServer((self.host, self.port), self._handler())

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def _root_page(self):
        return importlib.resources.read_text("spherecontrol.html", "main.html")

    def state_data(self):

        # Convert light data to hex format
        colors = []
        white_text = []
        for light_data in [self.bottom_lights, self.top_lights]:
            for i in range(light_data.shape[0]):
                colors.append(f"#{light_data[i, 0]:02x}{light_data[i, 1]:02x}{light_data[i, 2]:02x}")

                white_text.append(bool(np.all(light_data[i] < 100)))

        lights = {
            "colors": colors,
            "whiteText": white_text
        }


        # Mechanical data
        mechanical = {
            "stage": {
                "commanded": f"{self.stage_position.commanded:.2g}",
                "actual": f"{self.stage_position.actual:.2g}"
            },
            "sphere": {
                "commanded": f"{self.sphere_position.commanded:.2g}",
                "actual": f"{self.sphere_position.actual:.2g}"
            }
        }

        return {"lights": lights, "mechanical": mechanical}

    def _handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":

                    html = server._root_page()

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(html.encode())))
                    self.end_headers()
                    self.wfile.write(html.encode())

                elif self.path == "/state":
                    with server._lock:
                        payload = server.state_data()

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(payload).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # disable successful request logging

        return Handler

    def light_control(self, data: bytes):
        self.bottom_lights, self.top_lights = decode_light_command(data)

    def motor_control(self, data: bytes):
        pass

    def run(self):
        msg = f"Serving on http://{self.host}:{self.port}"
        print(msg)
        self.logger.info(msg)
        self._server.serve_forever()

    def run_in_thread(self):
        msg = f"Serving on http://{self.host}:{self.port}"
        print(msg)
        self.logger.info(msg)

        thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        thread.start()

    def shutdown(self):
        self._server.shutdown()
        self._server.server_close()


if __name__ == "__main__":
    server = GraphicsServer(port=8080)

    server.run()

