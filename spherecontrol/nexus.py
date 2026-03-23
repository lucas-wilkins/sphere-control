""" Combined interface, runs Qt window, an HTTP server, and writes to serial """
import threading

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from control_panel.display import Display
from firmware.lights.light_messages import LightMessageType
from graphicsserver import GraphicsServer
from serial_communication import SerialControl
from test_sequences.axis_sequence import AxisSequence
from test_sequences.base_sequence import TestSequenceSeries
from test_sequences.chase_sequence import ChaseSequence
from test_sequences.rainbow import Rainbows


class Nexus:
    def __init__(self, full_screen: bool=False, widget_size=24):
        # Properties
        self.manual_mode = False
        self.homed = False

        # Window
        app = QApplication()

        app.setStyleSheet(f"""
        QWidget {{ font-size: {widget_size}px; }}
        QPushButton {{ padding: {widget_size // 2}px {widget_size}px; }}
        """)

        self.control_panel = Display()
        if full_screen:
            self.control_panel.showFullScreen()
        else:
            self.control_panel.show()
            self.control_panel.setMinimumSize(QSize(800,600))

        # Server
        self.server = GraphicsServer()
        self.server.run_in_thread()
        self._stop_event: threading.Event | None = None

        # Serial
        self.devices = SerialControl.auto_assign()

        # Wire controls
        self.control_panel.light_test.connect(self.start_light_test)
        self.control_panel.combined_test.connect(self.start_combined_test)
        self.control_panel.home.connect(self.start_home)
        self.control_panel.imaging.connect(self.start_imaging_position)
        self.control_panel.stop_current.connect(self.stop)
        self.control_panel.enable_manual_mode.connect(self.enable_manual)
        self.control_panel.disable_manual_mode.connect(self.disable_manual)

        # Start Qt app
        app.exec()

    def lights_off(self):
        self.send_to_lights_and_server(bytes([LightMessageType.ALL_OFF.value]))

    def set_homed(self):
        self.is_homed = True

    def enable_manual(self):
        self.manual_mode = True

    def disable_manual(self):
        self.manual_mode = False

    def set_manual_control_allowed(self, allowed: bool):
        pass

    def send_to_lights_and_server(self, msg: bytes):
        self.devices.lights_serial.write(msg)
        self.server.light_control(msg)

    def start_light_test(self):
        sequencer = TestSequenceSeries(
            ChaseSequence(10),
            AxisSequence(axis=(1, 0, 0), color=(1, 0, 0)),
            AxisSequence(axis=(0, 1, 0), color=(0, 1, 0)),
            AxisSequence(axis=(0, 0, 1), color=(0, 0, 1)),
            Rainbows())

        self._stop_event = sequencer.run(
            self.send_to_lights_and_server, dt=0.05,
            on_stop=self.lights_off)

    def start_combined_test(self):
        pass

    def start_home(self):
        pass

    def start_imaging_position(self):
        pass

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()
            self.control_panel.set_stopped()

        # TODO Remove later
        self.control_panel.set_stopped()

if __name__ == "__main__":
    # nexus = Nexus(True)
    nexus = Nexus()