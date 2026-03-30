""" Combined interface, runs Qt window, an HTTP server, and writes to serial """
import threading

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from control_panel.display import Display, Page
from firmware.lights.light_messages import LightMessageType
from graphicsserver import GraphicsServer
from motor_control import MotorControl
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

        # Motor control
        self.stage_control = MotorControl(serial_object=self.devices.stage_serial, motor_type="Stage")
        self.stage_control.schedule_position_updates(self.update_stage_state)

        # Wire controls
        self.control_panel.sequence_light_test.connect(self.start_sequence_light_test)
        self.control_panel.axis_light_test.connect(self.start_axis_light_test)
        self.control_panel.rainbow_light_test.connect(self.start_rainbow_light_test)
        self.control_panel.full_light_test.connect(self.start_full_light_test)

        self.control_panel.home.connect(self.start_home)
        self.control_panel.imaging.connect(self.start_imaging_position)
        self.control_panel.stop_current.connect(self.stop)

        # Start Qt app
        app.exec()

    def update_stage_state(self, moving: bool, encoder: int, steps: int):
        self.control_panel.pages[Page.MAIN].stage_axis_encoder.setText(str(encoder))
        self.control_panel.pages[Page.MAIN].stage_axis_steps.setText(str(steps))
        self.control_panel.pages[Page.MAIN].stage_axis_moving.setText("Moving" if moving else "")

    def lights_off(self):
        self.send_to_lights_and_server(bytes([LightMessageType.ALL_OFF.value]))

    def send_to_lights_and_server(self, msg: bytes):
        self.devices.lights_serial.write(msg)
        self.server.light_control(msg)

    def run_light_test(self, sequencer):

        self._stop_event = sequencer.run(
            self.send_to_lights_and_server, dt=0.25,
            on_stop=self.lights_off)


    def start_full_light_test(self):
        self.run_light_test(TestSequenceSeries(
            ChaseSequence(10),
            AxisSequence(axis=(1, 0, 0), color=(1, 0, 0)),
            AxisSequence(axis=(0, 1, 0), color=(0, 1, 0)),
            AxisSequence(axis=(0, 0, 1), color=(0, 0, 1)),
            Rainbows()))

    def start_axis_light_test(self):
        self.run_light_test(TestSequenceSeries(
            AxisSequence(axis=(1, 0, 0), color=(1, 0, 0)),
            AxisSequence(axis=(0, 1, 0), color=(0, 1, 0)),
            AxisSequence(axis=(0, 0, 1), color=(0, 0, 1))))

    def start_rainbow_light_test(self):
        self.run_light_test(Rainbows())

    def start_sequence_light_test(self):
        self.run_light_test(ChaseSequence(4))


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
    nexus = Nexus(True)
