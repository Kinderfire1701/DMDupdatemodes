"""Imports from Ctypes package and customexceptions"""
import ctypes
import logging
from customexceptions import *
from PyQt5 import QtWidgets, QAxContainer
import sys

logging.basicConfig(filename='DMDGui.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DLPImage:
    """
    Class for images uploaded to the DMD.
    """
    
    def __init__(self, image_path):
        self.image_path = image_path

class DLPController:
    """
    Class for controlling a DLP (Digital Light Processing) device.

    Attributes:
        _dll (ctypes.WinDLL): Represents the DLL for interfacing with the DLP device.
        _dll.SetSWOverrideValue.argtypes (list):
            List of ctypes data types for the arguments of SetSWOverrideValue function.
        _dll.SetSWOverrideValue.restype (ctypes data type):
            Data type of the return value of SetSWOverrideValue function.
        _dll.SetSWOverrideEnable.argtypes (list):
            List of ctypes data types for the arguments of SetSWOverrideEnable function.
        _dll.SetSWOverrideEnable.restype (ctypes data type):
            Data type of the return value of SetSWOverrideEnable function.
    """

    def __init__(self, dll_path=r'C:\Windows\SysWOW64\D4100_usb.dll', COM_class='DDC4100.DDC4100Ctrl.1'):
        """
        Initialize the DLPController object.
        Uses the ctypes package to setup interactions with the API

        Args:
            dll_path (str): Path to the DLL file for interfacing with the DLP device.
            Defaults to 'D4100_usb.dll'
            com_class (str): Name of COM class, which can be found by searching for "DDC4100" in the Windows Registry Editor.
        """
        # initializing DLL API
        logging.debug("Attempting to setup API for use")
        self._dll = ctypes.CDLL(dll_path)
        self._dll.SetSWOverrideValue.argtypes = [ctypes.c_short, ctypes.c_short]
        self._dll.SetSWOverrideValue.restype = ctypes.c_short
        
        self._dll.SetSWOverrideEnable.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideEnable.restype = ctypes.c_short

        self._dll.GetSWOverrideValue.argtypes = []
        self._dll.GetSWOverrideValue.restype = ctypes.c_short
        
        logging.debug("Finished setting up DLL API")
        
        # initializing ActiveX API
        self._app = QtWidgets.QApplication([''])
        self._activex = QAxContainer.QAxWidget(COM_class)
        
        logging.debug("Finished setting up ActiveX API")

    def _set_sw_override_value(self, value):
        """
        Set the software override value.

        Args:
            value (int): The value to set for software override.

        Raises:
            SetSWOverrideValueError: If setting the software override value fails.
            To be handled outside the class.
        """
        value_short = ctypes.c_short(value)
        result = self._dll.SetSWOverrideValue(value_short,0)
        if result != 0:
            error_msg = ctypes.get_last_error()
            detailed_error_msg = f"Failed to set software switch override value. Error code: {result}. Error message: {error_msg}"
            logging.error(detailed_error_msg)
            exception = ValueError(detailed_error_msg)
            raise exception
    
        new_val = self._dll.GetSWOverrideValue()
        binary_override = bin(new_val)
        print(f'Software override value set to {new_val}')
        logging.debug(f'Software override value set to {new_val}')


    def _set_sw_override_enable(self, value):
        """
        Enable or disable the software override.

        Args:
            value (int): The value to enable or disable software override.

        Raises:
            EnableSWOverrideError: If enabling or disabling software override fails.
            To behandled outside class
        """
        value_short = ctypes.c_short(value)
        result = self._dll.SetSWOverrideEnable(value_short)
        print("Result of current action:", result)
        if result != 0:
            exception = EnableSWOverrideError(value)
            logging.error(f"Error setting software override: {str(exception)}")
            raise exception
        logging.debug(f'Software override enabled: {value}')

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
        
    def enable_override(self):
        """Enables software override for the DLP device settings and disables mechanical DIP switches. Class _set_sw_override_enable"""
        if self._dll.GetSWOverrideEnable(0) != 1:
            enable_value = 1
            self._set_sw_override_enable(enable_value)

    def disable_override(self):
        """Disables software override for the DLP device and enables mechanical DIP switches. Calls _set_sw_override_enable"""
        if self._dll.GetSWOverrideEnable() != 0:
            disable_value = 0
            self._set_sw_override_enable(disable_value)

    def set_single(self):
        """Set the DMD to single row update mode."""
        binary_input_value = 0x00 # 0000 0000
        print(type(binary_input_value))
        self._set_sw_override_value(binary_input_value)

    def set_dual(self):
        """Set the DMD to dual row update mode."""
        binary_input_value = 0x10 # 0001 0000
        self._set_sw_override_value(binary_input_value)

    def set_quad(self):
        """Set the DMD to quad row update mode."""
        binary_input_value = 0x30 # 0011 0000
        self._set_sw_override_value(binary_input_value)

    def set_global(self):
        """Set the DMD to global update mode."""
        binary_input_value = 0x20 # 0010 0000
        self._set_sw_override_value(binary_input_value)
        
    #def upload_frame(self):
    