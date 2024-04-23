class SetSWOverrideValueError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__("Failed to set SW override value: {}".format(hex(value)))

class EnableSWOverrideError(Exception):
    def __init__(self, value):
        if value == 1:
            super().__init__("Failed to Enable Software Override")
        else:
            super().__init__("Failed to Disable Software Override")
            
class ConnectDeviceError(Exception):
    def __init__(self):
        super().__init__("Failed to connect to USB device")
        
class BufferUploadError(Exception):
    def __init__(self, path):
        super().__init__(f"Failed to load buffer with image: {path}")