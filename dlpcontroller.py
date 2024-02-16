"""Imports from Ctypes packag and customexceptions"""
import ctypes
from customexceptions import SetSWOverrideValueError, EnableSWOverrideError

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

    def __init__(self, dll_path='D4100_usb.dll'):
        """
        Initialize the DLPController object.
        Uses the ctypes package to setup interactions with the API

        Args:
            dll_path (str): Path to the DLL file for interfacing with the DLP device.
            Defauls to 'D4100_usb.dll'
        """
        #initializing some stuff for the API
        self._dll = ctypes.WinDLL(dll_path)
        self._dll.SetSWOverrideValue.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideValue.restype = ctypes.c_short
        self._dll.SetSWOverrideEnable.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideEnable.restype = ctypes.c_short

    def _set_sw_override_value(self, value):
        """
        Set the software override value.

        Args:
            value (int): The value to set for software override.

        Raises:
            SetSWOverrideValueError: If setting the software override value fails.
            To be handled outside the class.
        """
        result = self._dll.SetSWOverrideValue(value)
        if result != 1:
            raise SetSWOverrideValueError(value)

    def _set_sw_override_enable(self, value):
        """
        Enable or disable the software override.

        Args:
            value (int): The value to enable or disable software override.

        Raises:
            EnableSWOverrideError: If enabling or disabling software override fails.
            To behandled outside class
        """
        result = self._dll.SetSWOverrideEnable(value)
        if result != 1:
            raise EnableSWOverrideError(value)

    def enable_updates(self):
        """Enable updates for the DLP device. Class _set_sw_override_enable"""
        enable_value = 1
        self._set_sw_override_enable(enable_value)

    def disable_updates(self):
        """Disable updates for the DLP device. Calls _set_sw_override_enable"""
        disable_value = 0
        self._set_sw_override_enable(disable_value)

    def set_single(self):
        """Set the DMD to single row update mode."""
        binary_input_value = 0x00 # 0000 0000
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
