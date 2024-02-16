import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox
from PySide6.QtGui import QPixmap
from dlpcontroller import DLPController
from customexceptions import EnableSWOverrideError, SetSWOverrideValueError

class MainWindow(QWidget):
    """
    Main window class for the DMD Update Mode GUI.

    Attributes:
        _curr_mode (str): The current update mode.
        _controller (DLPController): The DLP controller instance.
        button1 (QPushButton): Button for 'Global' update mode.
        button2 (QPushButton): Button for 'Single' update mode.
        button3 (QPushButton): Button for 'Dual' update mode.
        button4 (QPushButton): Button for 'Quad' update mode.
        label (QLabel): Label to display the current update mode.
        image_frame (QFrame): Frame to contain the image area.
        image_label (QLabel): Label to display the image.
    """
    def __init__(self):
        """
        Initializes the main window. Enables updates on the DLP controller and sets the
        Current update mode to global. Conditional error handling depending.
        """
        super().__init__()

        self.InitUI()
        self.loadImage('Global')
        self._curr_mode = "Global"
        self.label.setText(f'Current Update Mode: {self._curr_mode}')
        try:
            self._controller = DLPController()
            self._controller.enable_updates()
            #self._controller.set_global()
        except EnableSWOverrideError as exception:
            self.showErrorMessageBox(str(exception))
            sys.exit(1)
        except FileNotFoundError as exception:
            msg = """.dll file for API not found.
            Launching anyway, but DMD update mode cannot be changed!"""
            self.showErrorMessageBox(msg)
            self._controller = None

    def __del__(self):
        """
        Disables updates when the window is deleted.
        """
        try:
            self._controller.disable_updates()
        except EnableSWOverrideError as exception:
            self.showErrorMessageBox(str(exception))
            sys.exit(1)

    def InitUI(self):
        """
        Initializes the user interface.
        """
        self.setWindowTitle("DMD Update Mode GUI")
        self.setGeometry(100, 100, 500, 300)

        # Create main layout
        main_layout = QHBoxLayout()

        # Create button layout
        button_layout = QVBoxLayout()

        # Create buttons
        self.button1 = QPushButton('Global', self)
        self.button2 = QPushButton('Single', self)
        self.button3 = QPushButton('Dual', self)
        self.button4 = QPushButton('Quad', self)

        # Add buttons to button layout
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)
        button_layout.addWidget(self.button4)

        # Create layout for label and image
        label_image_layout = QVBoxLayout()

        # Create label for the most recently clicked button
        self.label = QLabel('Current Update Mode: None', self)
        label_image_layout.addWidget(self.label)

        # Create a frame for the image area
        self.image_frame = QFrame(self)
        self.image_frame.setFrameShape(QFrame.StyledPanel)

        # Create layout for image area
        image_layout = QVBoxLayout()
        self.image_label = QLabel("Image Area")
        self.image_label.setAlignment(Qt.AlignCenter)  # Align image_label in the center
        image_layout.addWidget(self.image_label)

        # Set the layout for the image frame
        self.image_frame.setLayout(image_layout)
        label_image_layout.addWidget(self.image_frame)

        # Add button layout and label/image layout to main layout
        main_layout.addLayout(button_layout)
        main_layout.addLayout(label_image_layout)

        # Set stretch factors
        label_image_layout.setStretch(0, 1)  # Label takes up 1 part
        label_image_layout.setStretch(1, 4)  # Image area takes up 4 parts

        # Add main layout to window
        self.setLayout(main_layout)

        # Connect buttons to a slot
        self.button1.clicked.connect(self.buttonClicked)
        self.button2.clicked.connect(self.buttonClicked)
        self.button3.clicked.connect(self.buttonClicked)
        self.button4.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        """
        Handles button click events.
        """
        sender = self.sender()
        if self._curr_mode != sender.text() and self._controller is not None:
            try:
                if sender.text() == 'Global':
                    self._controller.set_global()
                elif sender.text() == 'Single':
                    self._controller.set_single()
                elif sender.text() == 'Dual':
                    self._controller.set_dual()
                elif sender.text() == 'Quad':
                    self._controller.set_quad()
            except SetSWOverrideValueError as exception:
                self.showErrorMessageBox(str(exception))
        self._curr_mode = sender.text()
        self.label.setText(f'Current Update Mode: {self._curr_mode}')
        self.loadImage(sender.text())

    def loadImage(self, button_text):
        """
        Loads and displays the image based on the selected mode.

        Args:
            button_text (str): The text of the image to display
        """
        image_path = None
        if button_text == 'Global':
            image_path = 'Global.jpg'
        elif button_text == 'Single':
            image_path = 'Single.jpg'
        elif button_text == 'Dual':
            image_path = 'Dual.jpg'
        elif button_text == 'Quad':
            image_path = 'Quad.jpg'

        if image_path:
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)

    def showErrorMessageBox(self, message):
        """
        Shows an error message box with the given message.

        Args:
            message (str): The error message to display.
        """
        error_box = QMessageBox()
        error_box.setWindowTitle("Error")
        error_box.setIcon(QMessageBox.Critical)
        error_box.setText(message)
        error_box.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
