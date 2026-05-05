""" Combined interface, runs Qt window, an HTTP server, and writes to serial """
import logging
import sys
import threading

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from configuration import config
from control_panel.display import Display, Page
from control_server import ControlServer
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
        self.app = QApplication()

        self.app.setStyleSheet(f"""
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

        # Window threading stuff
        self._stop_event: threading.Event | None = None

        # Serial
        self.devices = SerialControl.auto_assign()

        # Motor control
        self.stage_control = MotorControl(
            serial_object=self.devices.stage_serial,
            motor_type="Stage",
            steps_per_revolution=config.stage_steps_per_revolution,
            encoder_positions_per_revolution=config.stage_encoder_positions_per_revolution)

        self.stage_control.schedule_position_updates(self.update_stage_state)

        self.sphere_control = MotorControl(
            serial_object=self.devices.sphere_serial,
            motor_type="Sphere",
            steps_per_revolution=config.sphere_steps_per_revolution,
            encoder_positions_per_revolution=config.sphere_encoder_positions_per_revolution)

        self.sphere_control.schedule_position_updates(self.update_sphere_state)

        # Wire controls
        ## Light test
        self.control_panel.sequence_light_test.connect(self.start_sequence_light_test)
        self.control_panel.axis_light_test.connect(self.start_axis_light_test)
        self.control_panel.rainbow_light_test.connect(self.start_rainbow_light_test)
        self.control_panel.full_light_test.connect(self.start_full_light_test)

        ## Motor control
        self.control_panel.pages[Page.MAIN].stage_increment.increment_requested.connect(self.on_stage_increment)
        self.control_panel.pages[Page.MAIN].sphere_increment.increment_requested.connect(self.on_sphere_increment)

        ## Misc
        self.control_panel.rough_home.connect(self.rough_home)
        self.control_panel.precise_home.connect(self.precise_home)
        self.control_panel.origin.connect(self.set_origin)
        self.control_panel.imaging.connect(self.start_imaging_position)
        self.control_panel.stop_current.connect(self.stop)

        self.control_panel.pages[Page.SETTINGS].exit_button.clicked.connect(self.on_exit_clicked)

        # Set up configuration
        self.sphere_control.set_limits(config.sphere_axis_low, config.sphere_axis_high)
        self.sphere_control.get_limits()

        # Set up control server
        self.control_server = ControlServer(
            self.stage_control.goto_steps,
            self.sphere_control.goto_steps,
            self.send_to_lights_and_server,
            self.is_moving)

        self.control_server.serve()

        # Start Qt app
        self.app.exec()

    def update_stage_state(self, moving: bool, encoder: int, steps: int):
        self.control_panel.pages[Page.MAIN].stage_axis_encoder.setText(str(encoder))
        self.control_panel.pages[Page.MAIN].stage_axis_steps.setText(str(steps))
        self.control_panel.pages[Page.MAIN].stage_axis_moving.setText("Moving" if moving else "")

    def update_sphere_state(self, moving: bool, encoder: int, steps: int):
        self.control_panel.pages[Page.MAIN].sphere_axis_encoder.setText(str(encoder))
        self.control_panel.pages[Page.MAIN].sphere_axis_steps.setText(str(steps))
        self.control_panel.pages[Page.MAIN].sphere_axis_moving.setText("Moving" if moving else "")

    def lights_off(self):
        self.send_to_lights_and_server(bytes([LightMessageType.ALL_OFF.value]))

    def send_to_lights_and_server(self, msg: bytes):
        self.devices.lights_serial.write(msg)
        self.server.light_control(msg)

    def run_light_test(self, sequencer):

        self._stop_event = sequencer.run(
            self.send_to_lights_and_server, dt=0.25,
            on_stop=self.lights_off)

    def on_stage_increment(self, increment: int):
        self.increment(self.stage_control, increment)

    def on_sphere_increment(self, increment: int):
        self.increment(self.sphere_control, increment)

    @staticmethod
    def increment(motor_control: MotorControl, increment: int):
        with motor_control.paused():
            motor_control.increment_steps(increment)

    def is_moving(self):
        """ Get whether we are moving """
        stage_moving, _, _ = self.stage_control.get_state()
        sphere_moving, _, _ = self.sphere_control.get_state()

        return stage_moving or sphere_moving

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

    def precise_home(self):
        # home(config.sphere_axis_home_position,
        #      config.homing_n_steps_during_search,
        #      config.homing_search_radius_steps,
        #      self.sphere_control.
        #      )
        pass

    def rough_home(self):
        """ Simple method of finding the home position """
        with self.stage_control.paused():
            self.stage_control.move_to_encoder_position(config.stage_axis_home_position, settle_time_seconds=0.5)
            self.stage_control.set_home()

        with self.sphere_control.paused():
            self.sphere_control.move_to_encoder_position(config.sphere_axis_home_position, settle_time_seconds=0.5)
            self.sphere_control.set_home()

        self.control_panel.set_stopped()

    def set_origin(self):
        """ Set the current motor steps to zero"""
        with self.stage_control.paused():
            self.stage_control.set_home()

        with self.sphere_control.paused():
            self.sphere_control.set_home()

        self.control_panel.set_stopped()

    def start_imaging_position(self):
        pass

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()
            self.control_panel.set_stopped()

        # TODO Remove later
        self.control_panel.set_stopped()

    def on_exit_clicked(self):
        """ Do exit """
        self.control_server.shutdown()
        self.server.shutdown()
        self.app.shutdown()
        sys.exit()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s, %(name)s: %(message)s"
    )

    nexus = Nexus(False)
