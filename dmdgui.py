import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from dlpcontroller import DLPController
from customexceptions import EnableSWOverrideError, SetSWOverrideValueError
import logging
import sys

logging.basicConfig(filename='DMDGui.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainWindow(tk.Tk):
    """
    Main window class for the DMD Update Mode GUI.

    Attributes:
        _curr_mode (str): The current update mode.
        _controller (DLPController): The DLP controller instance.
        image_label (tk.Label): Label to display the image.
    """
    def __init__(self):
        """
        Initializes the main window. Enables updates on the DLP controller and sets the
        Current update mode to global. Conditional error handling depending.
        """
        super().__init__()

        logger.debug("Initializing the main window.")

        self._curr_mode = None
        self._controller = None

        self.init_ui()
        self.load_image('Global')

        try:
            self._controller = DLPController()
            self._controller.enable_override()
            logger.debug("Updates enabled successfully.")
        except EnableSWOverrideError as exception:
            logger.error(f"Error enabling updates: {exception}")
            self.show_error_message_box(str(exception))
            sys.exit(1)
        except FileNotFoundError as exception:
            logger.error(f"File not found: {exception}")
            msg = """.dll file for API not found.
            Launching anyway, but DMD update mode cannot be changed!"""
            self.show_error_message_box(msg)

    def __del__(self):
        """
        Disables updates when the window is deleted.
        """
        try:
            self._controller.disable_override()
        except EnableSWOverrideError as exception:
            self.show_error_message_box(str(exception))
            sys.exit(1)

    def init_ui(self):
        """
        Initializes the user interface.
        """
        self.title("DMD Update Mode GUI")
        self.geometry("500x300")

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.LEFT, padx=10)

        # Create buttons
        button_texts = ['Global', 'Single', 'Dual', 'Quad']
        for text in button_texts:
            button = tk.Button(button_frame, text=text, command=lambda t=text: self.button_clicked(t))
            button.pack(side=tk.TOP, pady=5)

        # Create label frame
        label_frame = tk.Frame(main_frame)
        label_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create label for the most recently clicked button
        self.label = tk.Label(label_frame, text='Current Update Mode: None')
        self.label.pack(side=tk.TOP, pady=10)

        # Create a frame for the image area
        self.image_frame = tk.Frame(label_frame, relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        # Create label for image
        self.image_label = tk.Label(self.image_frame, text="Image Area")
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def button_clicked(self, button_text):
        """
        Handles button click events.

        Args:
            button_text (str): The text of the clicked button.
        """
        logger.debug(f"Button clicked: {button_text}")

        if self._curr_mode != button_text and self._controller is not None:
            try:
                if button_text == 'Global':
                    self._controller.set_global()
                    logger.debug("Setting update mode to Global")
                elif button_text == 'Single':
                    self._controller.set_single()
                    logger.debug("Setting update mode to Single")
                elif button_text == 'Dual':
                    self._controller.set_dual()
                    logger.debug("Setting update mode to Dual")
                elif button_text == 'Quad':
                    self._controller.set_quad()
                    logger.debug("Setting update mode to Quad")
            except SetSWOverrideValueError as exception:
                logger.error(f"Error setting update mode: {exception}")
                self.show_error_message_box(str(exception))
        self._curr_mode = button_text
        self.label.config(text=f'Current Update Mode: {self._curr_mode}')
        self.load_image(button_text)

    def load_image(self, button_text):
        """
        Loads and displays the image based on the selected mode.

        Args:
            button_text (str): The text of the image to display.
        """
        image_path = f"{button_text}.jpg"
        try:
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            self.show_error_message_box(f"Image file not found: {image_path}")

    def show_error_message_box(self, message):
        """
        Shows an error message box with the given message.

        Args:
            message (str): The error message to display.
        """
        messagebox.showerror("Error", message)

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()