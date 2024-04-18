"""Imports from Ctypes package and customexceptions"""
import ctypes
import logging
from customexceptions import SetSWOverrideValueError, EnableSWOverrideError

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

    def __init__(self, dll_path='C:\Windows\SysWOW64\D4100_usb.dll'):
        """
        Initialize the DLPController object.
        Uses the ctypes package to setup interactions with the API

        Args:
            dll_path (str): Path to the DLL file for interfacing with the DLP device.
            Defaults to 'D4100_usb.dll'
        """
        #initializing some stuff for the API
        logging.debug("Attempting to setup API for use")
        self._dll = ctypes.CDLL(dll_path)
        self._dll.SetSWOverrideValue.argtypes = [ctypes.c_short, ctypes.c_short]
        self._dll.SetSWOverrideValue.restype = ctypes.c_short
        self._dll.SetSWOverrideEnable.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideEnable.restype = ctypes.c_short
        logging.debug("Finished setting up for API use")

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
        print("Current SW override", bin(self._dll.GetSWOverrideEnable(0)))
        print("Current SW override Value", bin(self._dll.GetSWOverrideValue(0)))
        print("Result of current action:", result)
        if result != 0:
            error_msg = ctypes.get_last_error()
            detailed_error_msg = f"Failed to set software switch override value. Error code: {result}. Error message: {error_msg}"
            logging.error(detailed_error_msg)
            exception = ValueError(detailed_error_msg)
            raise exception
    
        logging.debug(f'Software override value set to {value}')


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


    def enable_updates(self):
        """Enable updates for the DLP device. Class _set_sw_override_enable"""
        if self._dll.GetSWOverrideEnable(0) != 1:
            print("Enabling Override")
            enable_value = 1
            self._set_sw_override_enable(enable_value)
            print("New", bin(self._dll.GetSWOverrideEnable(0)))

    def disable_updates(self):
        """Disable updates for the DLP device. Calls _set_sw_override_enable"""
        if self._dll.GetSWOverrideEnable() != 0:
            disable_value = 0
            print("Disabling Override")
            print("value = ", bin(disable_value))
            print("Current SW override", bin(self._dll.GetSWOverrideEnable(0)))
            self._set_sw_override_enable(disable_value)
            print("New", bin(self._dll.GetSWOverrideEnable(0)))
            print("Current SW override Value", bin(self._dll.GetSWOverrideValue(0)))

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