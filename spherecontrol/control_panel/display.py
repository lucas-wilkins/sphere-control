import sys
from enum import Enum

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, \
    QPushButton, QGridLayout, QLabel

_default_status = "Ready"

class NavigationState(Enum):
    NORMAL = "normal"
    TEST_RUNNING = "running"

class QRightLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignRight)

class MainPage(QWidget):
    go_to_settings = Signal()
    stop = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.base_layout = QVBoxLayout()
        self.setLayout(self.base_layout)

        self.navigation_widget = QWidget()
        self.navigation_layout = QHBoxLayout()
        self.navigation_widget.setLayout(self.navigation_layout)

        self.data_widget = QWidget()
        self.data_layout = QGridLayout()
        self.data_widget.setLayout(self.data_layout)

        self.stage_axis_actual = QLabel()
        self.stage_axis_commanded = QLabel()

        self.sphere_axis_actual = QLabel()
        self.sphere_axis_commanded = QLabel()

        self.lights = QLabel()

        self.data_layout.addWidget(QLabel("Actual"), 0, 1)
        self.data_layout.addWidget(QLabel("Commanded"), 0, 2)

        self.data_layout.addWidget(QRightLabel("Stage"), 1, 0)
        self.data_layout.addWidget(self.stage_axis_actual, 1, 1)
        self.data_layout.addWidget(self.stage_axis_commanded, 1, 2)

        self.data_layout.addWidget(QRightLabel("Sphere"), 2, 0)
        self.data_layout.addWidget(self.sphere_axis_actual, 2, 1)
        self.data_layout.addWidget(self.sphere_axis_commanded, 2, 2)

        self.data_layout.addWidget(QRightLabel("Lights"), 3, 0)
        self.data_layout.addWidget(self.lights, 3, 1)

        # Navigation Bar

        self.manual_label = QLabel("")
        self.navigation_layout.addWidget(self.manual_label)

        self.status_label = QLabel(_default_status)
        self.navigation_layout.addWidget(self.status_label)

        self.navigation_layout.addSpacerItem(QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.navigation_button = QPushButton("Settings")
        self.navigation_button.clicked.connect(self.navigation_button_clicked)
        self.navigation_layout.addWidget(self.navigation_button)

        # Put things in place

        self.base_layout.addWidget(self.data_widget)
        self.base_layout.addSpacerItem(QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.base_layout.addWidget(self.navigation_widget)

        self.navigation_state = NavigationState.NORMAL

    def set_navigation_state(self, state: NavigationState):
        match state:
            case NavigationState.NORMAL:
                self.navigation_button.setText("Settings")
            case NavigationState.TEST_RUNNING:
                self.navigation_button.setText("Stop")
        self.navigation_state = state


    def navigation_button_clicked(self):
        match self.navigation_state:
            case NavigationState.NORMAL:
                self.go_to_settings.emit()
            case NavigationState.TEST_RUNNING:
                self.stop.emit()

    def set_stopped(self):
        self.set_navigation_state(NavigationState.NORMAL)


class SettingsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


        self.base_layout = QVBoxLayout()
        self.setLayout(self.base_layout)

        self.button_widget = QWidget()
        self.button_layout = QGridLayout()

        self.manual_mode = QPushButton("Manual Positioning")
        self.manual_mode.setCheckable(True)

        self.home = QPushButton("Home")
        self.imaging = QPushButton("Imaging Position")
        self.light_test = QPushButton("Light Diagnostic")
        self.combined_test = QPushButton("Combined Diagnostic")
        self.exit_button = QPushButton("Exit Interface")

        self.button_layout.addWidget(self.manual_mode, 0, 0)
        self.button_layout.addWidget(self.home, 1, 0)
        self.button_layout.addWidget(self.imaging, 2, 0)
        self.button_layout.addWidget(self.light_test, 3, 0)
        self.button_layout.addWidget(self.combined_test, 4, 0)
        self.button_layout.addWidget(self.exit_button, 5, 0)

        self.button_widget.setLayout(self.button_layout)


        self.base_layout.addWidget(self.button_widget)

        self.navigation_widget = QWidget()
        self.navigation_layout = QHBoxLayout()
        self.navigation_widget.setLayout(self.navigation_layout)


        self.navigation_layout.addSpacerItem(QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_button = QPushButton("Back")
        self.navigation_layout.addWidget(self.main_button)

        self.base_layout.addSpacerItem(QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.base_layout.addWidget(self.navigation_widget)

        self.exit_button.clicked.connect(sys.exit)


class Page(Enum):
    MAIN = "main"
    SETTINGS = "settings"

class Display(QMainWindow):
    stop_current = Signal()
    light_test = Signal()
    combined_test = Signal()
    home = Signal()
    imaging = Signal()
    enable_manual_mode = Signal()
    disable_manual_mode = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)



        self.pages = {
            Page.MAIN: MainPage(),
            Page.SETTINGS: SettingsPage()
        }

        self.pages[Page.MAIN].go_to_settings.connect(self.on_go_to_settings)
        self.pages[Page.MAIN].stop.connect(self.on_stop_requested)
        self.pages[Page.SETTINGS].main_button.clicked.connect(self.on_go_to_main)
        self.pages[Page.SETTINGS].light_test.clicked.connect(self.on_run_light_test)
        self.pages[Page.SETTINGS].home.clicked.connect(self.on_run_home)
        self.pages[Page.SETTINGS].imaging.clicked.connect(self.on_run_imaging)
        self.pages[Page.SETTINGS].combined_test.clicked.connect(self.on_run_combined_test)
        self.pages[Page.SETTINGS].manual_mode.clicked.connect(self.on_manual_clicked)

        self.selected_page: Page = Page.MAIN


        self.setCentralWidget(self.pages[Page.MAIN])

    def set_page(self, window_choice: Page):
        if self.selected_page != window_choice:
            self.pages[self.selected_page] = self.takeCentralWidget()
            self.setCentralWidget(self.pages[window_choice])
            self.selected_page = window_choice

    def on_manual_clicked(self):
        if self.pages[Page.SETTINGS].manual_mode.isChecked():
            self.enable_manual_mode.emit()
            self.pages[Page.MAIN].manual_label.setText("[MANUAL ENABLED]")
        else:
            self.disable_manual_mode.emit()
            self.pages[Page.MAIN].manual_label.setText("")

    def run_settings_procedure(self):
        self.set_page(Page.MAIN)
        self.pages[Page.MAIN].set_navigation_state(NavigationState.TEST_RUNNING)

    def set_status(self, status: str):
        self.pages[Page.MAIN].status_label.setText(status)

    def on_go_to_main(self):
        self.set_page(Page.MAIN)

    def on_go_to_settings(self):
        self.set_page(Page.SETTINGS)

    def on_run_light_test(self):
        self.set_status("Running light test...")
        self.light_test.emit()
        self.run_settings_procedure()

    def on_run_combined_test(self):
        self.set_status("Running combined test...")
        self.combined_test.emit()
        self.run_settings_procedure()

    def on_run_home(self):
        self.set_status("Homing...")
        self.home.emit()
        self.run_settings_procedure()

    def on_run_imaging(self):
        self.set_status("Positioning...")
        self.imaging.emit()
        self.run_settings_procedure()

    def on_stop_requested(self):
        self.stop_current.emit()

    def set_stopped(self):
        self.pages[Page.MAIN].set_navigation_state(NavigationState.NORMAL)
        self.set_status(_default_status)

if __name__ == "__main__":

    app = QApplication()

    widget = Display()
    widget.show()

    app.exec()