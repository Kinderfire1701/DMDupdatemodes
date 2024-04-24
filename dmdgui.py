import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from dlpcontroller import DLPControllerActiveX, DLPControllerDLL
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
        _interface (str): The current interface being used ('ActiveX' or 'DLL').
        interface_label (tk.Label): Label to display the current interface.
        selected_image_label (tk.Label): Label to display the selected image.
        selected_image_path_label (tk.Label): Label to display the path of the selected image.
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
        self._interface = 'ActiveX'  # Default interface

        self.init_ui()
        self.load_image('Global')

        try:
            if self._interface == 'ActiveX':
                self._controller = DLPControllerActiveX()
            elif self._interface == 'DLL':
                self._controller = DLPControllerDLL()
                
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
        if self._controller:
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
        self.geometry("1200x500")

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create label to display the current interface
        self.interface_label = tk.Label(main_frame, text=f'Current Interface: {self._interface}')
        self.interface_label.pack(side=tk.TOP, pady=10, anchor=tk.NW)

        # Create button to switch interface
        switch_button = tk.Button(main_frame, text='Switch Interface', command=self.switch_interface)
        switch_button.pack(side=tk.TOP, pady=5, anchor=tk.NW)

        # Create button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.LEFT, padx=10)

        # Create buttons
        button_texts = ['Global', 'Single', 'Dual', 'Quad']
        for text in button_texts:
            button = tk.Button(button_frame, text=text, command=lambda t=text: self.button_clicked(t))
            button.pack(side=tk.TOP, pady=5)

        # Create label frame for selected image and its path
        selected_image_frame = tk.Frame(main_frame)
        selected_image_frame.pack(side=tk.RIGHT, padx=10)

        # Create label for selected image
        self.selected_image_label = tk.Label(selected_image_frame, text="Selected Image")
        self.selected_image_label.pack(side=tk.TOP, pady=5)

        # Create label for selected image path
        self.selected_image_path_label = tk.Label(selected_image_frame, text="")
        self.selected_image_path_label.pack(side=tk.TOP, pady=5)

        # Create a frame for the image area
        self.image_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create label for image
        self.image_label = tk.Label(self.image_frame, text="Image Area")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Create a button to load an image
        load_image_button = tk.Button(button_frame, text='Load Image', command=self.load_image_button_clicked)
        load_image_button.pack(side=tk.TOP, pady=5)
    
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
        
    def switch_interface(self):
        """
        Switches between ActiveX and DLL interfaces.
        """
        if self._interface == 'ActiveX':
            self._interface = 'DLL'
            logger.debug("Switching interface to DLL")
        else:
            self._interface = 'ActiveX'
            logger.debug("Switching interface to ActiveX")
                        
        # Delete current controller instance
        del self._controller
        
        # Create new controller instance
        try:
            if self._interface == 'ActiveX':
                self._controller = DLPControllerActiveX()
            elif self._interface == 'DLL':
                self._controller = DLPControllerDLL()
                
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
        
        # Update interface label
        self.interface_label.config(text=f'Current Interface: {self._interface}')
        
    def load_image_button_clicked(self):
        """
        Handles the click event of the load image button.
        """
        # Prompt user to select an image file
        image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        
        if image_path:
            try:
                # Load image into DMD
                self._controller.load_image_buffer(image_path)
                logger.debug("Image loaded into DMD successfully.")
                
                # Display the loaded image
                self.display_selected_image(image_path)
                
            except Exception as e:
                logger.error(f"Error loading image: {e}")
                self.show_error_message_box(f"Error loading image: {e}")
    
    def display_selected_image(self, image_path):
        """
        Display the selected image.

        Args:
            image_path (str): The path of the selected image.
        """
        try:
            # Display the selected image
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            self.selected_image_label.config(image=photo)
            self.selected_image_label.image = photo  # Keep a reference to prevent garbage collection
            
            # Display the path of the selected image
            self.selected_image_path_label.config(text=f"Selected Image Path: {image_path}")
        except FileNotFoundError:
            logger.error(f"Selected image file not found: {image_path}")
            self.show_error_message_box(f"Selected image file not found: {image_path}")

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()