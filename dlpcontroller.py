import ctypes
from customexceptions import SetSWOverrideValueError, EnableSWOverrideError

class DLPController:
    def __init__(self, dll_path='D4100_usb.dll'):
        #initializing some info about the class
        self._dll = ctypes.WinDLL(dll_path)
        self._dll.SetSWOverrideValue.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideValue.restype = ctypes.c_short
        self._dll.SetSWOverrideEnable.argtypes = [ctypes.c_short]
        self._dll.SetSWOverrideEnable.restype = ctypes.c_short

    def _set_sw_override_value(self, value):
        result = self._dll.SetSWOverrideValue(value)
        if result != 1:
            raise SetSWOverrideValueError(value)

    def _set_sw_override_enable(self, value):
        result = self._dll.SetSWOverrideEnable(value)
        if result != 1:
            raise EnableSWOverrideError(value)

    def enable_updates(self):
        enable_value = 1
        self._set_sw_override_enable(enable_value)

    def disable_updates(self):
        disable_value = 0
        self._set_sw_override_enable(disable_value)

    def set_single(self):
        binary_input_value = 0x00 # 0000 0000
        self._set_sw_override_value(binary_input_value)

    def set_dual(self):
        binary_input_value = 0x10 # 0001 0000
        self._set_sw_override_value(binary_input_value)

    def set_quad(self):
        binary_input_value = 0x30 # 0011 0000
        self.set_sw_override_value(binary_input_value)

    def set_global(self):
        binary_input_value = 0x20 # 0010 0000
        self._set_sw_override_value(binary_input_value)