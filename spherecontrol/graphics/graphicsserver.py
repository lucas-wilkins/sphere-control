import threading
import json
import logging


import numpy as np
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from lightdata import light_data




class GraphicsServer:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port


        self.top_lights = np.zeros((light_data.top.shape[0], 3), dtype=np.uint8)
        self.bottom_lights = np.zeros((light_data.bottom.shape[0], 3), dtype=np.uint8)

        self._lock = threading.Lock()

        self._server = ThreadingHTTPServer(
            (self.host, self.port),
            self._handler()
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def _root_page(self):
        with open("html/main.html", 'r') as file:
            return file.read()

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
                        payload = dict(server._state)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(payload).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        return Handler



    def light_control(self, data: bytes):
        pass

    def motor_control(self, data: bytes):
        pass

    def serve_forever(self):
        self.logger.info(f"Serving on http://{self.host}:{self.port}")
        self._server.serve_forever()

    def shutdown(self):
        self._server.shutdown()
        self._server.server_close()


if __name__ == "__main__":
    server = GraphicsServer(port=8080)

    # def serial_thread():
    #     # Read in serial
    #
    # threading.Thread(target=serial_thread, daemon=True).start()

    server.serve_forever()

