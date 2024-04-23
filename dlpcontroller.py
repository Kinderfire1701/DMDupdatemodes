"""Imports from Ctypes package and customexceptions"""
import ctypes
import logging
from customexceptions import *
from PyQt5 import QtWidgets, QAxContainer
import sys

logging.basicConfig(filename='DMDGui.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import abc

class DLPControllerBase(abc.ABC):
    """
    Abstract base class for controlling a DLP (Digital Light Processing) device.

    Attributes:
        _dll: Represents the DLL or ActiveX interface for interfacing with the DLP device.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def _set_sw_override_value(self, value):
        """
        Set the software override value.
        """
        pass

    @abc.abstractmethod
    def _set_sw_override_enable(self, value):
        """
        Enable or disable the software override.
        """
        pass

    def enable_override(self):
        """Enables software override for the DLP device settings and disables mechanical DIP switches. Class _set_sw_override_enable"""
        enable_value = 1
        self._set_sw_override_enable(enable_value)

    def disable_override(self):
        """Disables software override for the DLP device and enables mechanical DIP switches. Calls _set_sw_override_enable"""
        disable_value = 0
        self._set_sw_override_enable(disable_value)

    def set_single(self):
        """Set the DMD to single row update mode."""
        binary_input_value = 0x00  # Represents the binary value for single row update mode
        self._set_sw_override_value(binary_input_value)

    def set_dual(self):
        """Set the DMD to dual row update mode."""
        binary_input_value = 0x10  # Represents the binary value for dual row update mode
        self._set_sw_override_value(binary_input_value)

    def set_quad(self):
        """Set the DMD to quad row update mode."""
        binary_input_value = 0x30  # Represents the binary value for quad row update mode
        self._set_sw_override_value(binary_input_value)

    def set_global(self):
        """Set the DMD to global update mode."""
        binary_input_value = 0x20  # Represents the binary value for global update mode
        self._set_sw_override_value(binary_input_value)

class DLPControllerActiveX(DLPControllerBase):
    """
    Class for controlling a DLP (Digital Light Processing) device using ActiveX.

    Attributes:
        _app (QtWidgets.QApplication): Represents the PyQt application instance.
        _activex (QAxContainer.QAxWidget): Represents the ActiveX widget for interfacing with the DLP device.
    """

    def __init__(self, COM_class='DDC4100.DDC4100Ctrl.1'):
        """
        Initialize the DLPControllerActiveX object.

        Args:
            com_class (str): Name of COM class, which can be found by searching for "DDC4100" in the Windows Registry Editor.
        """
        super().__init__()

        # initializing ActiveX API
        self._app = QtWidgets.QApplication([''])
        self._activex = QAxContainer.QAxWidget(COM_class)
        
        logging.debug("Finished setting up ActiveX API")

    def _set_sw_override_value(self, value):
        """
        Set the software override value using ActiveX.
        """
        try:
            self._activex.dynamicCall("SetSWOverrideValue(short)", value)
            new_val = self._activex.dynamicCall("GetSWOverrideValue()")
            binary_override = bin(new_val)
            print(f'Software override value set to {binary_override}')
            logging.debug(f'Software override value set to {binary_override}')
        except SetSWOverrideValueError as e:
            logging.error(e)
            raise e


    def _set_sw_override_enable(self, value):
        """
        Enable or disable the software override using ActiveX.
        """
        try:
            result = self._activex.dynamicCall("SetSWOverrideEnable(short)", value)
            logging.debug(f'Software override enabled: {value}')
            return result
        except EnableSWOverrideError as e:
            logging.error(e)
            raise e
        
    def connect_device(self, id = 1, bin_path = r'C:\Program Files (x86)\D4100Explorer\D4100_GUI_FPGA.bin'):
        """
        Opens a connection to the USB device
        
        Args:
            value (int): Identifies the USB device, allowing for multiple boards to be connected.
                         Defaults to 1.
            bin_path (str): Location of .bin file that initializes the APPS_FPGA code.
                            The file is named "usb_main.bin" in older versions of the API and 
                            "D4100_GUI_FPGA.bin" in newer versions.
        """
        
        logging.debug("Attempting to connect to USB device")
        
        try:
            self.device_numbers = self._activex.dynamicCall("GetNumDevices( )")
            self._activex.dynamicCall("ConnectDevice(short, LPCTSTR)", id, bin_path)
            logging.debug(f'Device {id} of {self.device_numbers} successfully connected')  
        except ConnectDeviceError as e:
            logging.debug(e)
    
    def load_image_buffer(self, image_path, mirrored = False):
        """
        Converts image from several formats (bmp, jpg, gif, or bin) to a binary file and
        then loads binary file to image buffer of ActiveX controller
        
        Args:
            image_path (str): Location of binary image in bmp, jpg, gif, or bin format.
            mirrored (bool): If set to True, a mirrored image will also be prepared for the buffer.
        """
        
        mirror_value = int(mirrored) # any value other than 0 will enable the mirror feature, not specifically 1   
        result = self._activex.dynamicCall(f"FileToFrameBuffer({image_path}, {mirror_value})")
        
        if result != 1: 
            exception = BufferUploadError(image_path)
            logging.error(f"Error uploading image: {str(exception)}")
            raise exception
        else:
            logging.debug(f"Image uploaded from {image_path}")
        
    def load_buffer_DMD(self, block_number = 17, reset = True, Load4 = False):
        """
        Loads image from ActiveX controller buffer to a block of mirrors or all mirrors on DMD device.
        
        Args:
            block_number (int): Integers 1 to 16 designate blocks of mirrors on the DMD. This selects which block is updated.
            If set greater than 16, then the image is globally loaded to the whole DMD
            reset (bool): If enabled, then a write (reset) is automatically performed after the image is loaded from the buffer to the DMD.
            Load4 (bool): If enabled, activates a setting on the DMD that simulatenously loads four row using the same row data. 
                          Doing so sacrifices vertical resolution in exchange for faster loading times. Turned off by default.
        """
        
        reset_value = int(reset)
        Load4_value = int(Load4)
        result = self._activex.dynamicCall(f"LoadToDMD({block_number}, {reset_value}, {Load4_value})")   
        if result != 1: 
            logging.error("Error uploading image: Failed to load image from buffer to DMD device")
        else:
            logging.debug("Loaded image from ActiveX buffer to DMD device")
            
           
        
    def load_movie_buffer(self):
        """
        
        """
        pass

class DLPControllerDLL(DLPControllerBase):
    """
    Class for controlling a DLP (Digital Light Processing) device using DLL.

    Attributes:
        _dll (ctypes.WinDLL): Represents the DLL for interfacing with the DLP device.
    """

    def __init__(self, dll_path=r'C:\Windows\SysWOW64\D4100_usb.dll'):
        """
        Initialize the DLPControllerDLL object.

        Args:
            dll_path (str): Path to the DLL file for interfacing with the DLP device.
            Defaults to 'D4100_usb.dll'
        """
        super().__init__()

        # initializing DLL API
        logging.debug("Attempting to setup DLL API for use")
        self._dll = ctypes.CDLL(dll_path)
        self._dll.SetSWOverrideValue.argtypes = [ctypes.c_short, ctypes.c_short]
        self._dll.SetSWOverrideValue.restype = ctypes.c_short
        
        self._dll.SetSWOverrideEnable.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideEnable.restype = ctypes.c_short

        self._dll.GetSWOverrideValue.argtypes = []
        self._dll.GetSWOverrideValue.restype = ctypes.c_short
        
        logging.debug("Finished setting up DLL API")

    def _set_sw_override_value(self, value):
        """
        Set the software override value using DLL.
        """
        try:
            self._dll.SetSWOverrideValue(value, 0)
            new_val = self._dll.GetSWOverrideValue()
            binary_override = bin(new_val)
            print(f'Software override value set to {binary_override}')
            logging.debug(f'Software override value set to {binary_override}')
        except SetSWOverrideValueError as e:
            logging.error(e)
            raise e


    def _set_sw_override_enable(self, value):
        """
        Enable or disable the software override using DLL.
        """
        try:
            result = self._dll.SetSWOverrideEnable(value)
            logging.debug(f'Software override enabled: {value}')
            return result
        except EnableSWOverrideError as e:
            logging.error(e)
            raise e