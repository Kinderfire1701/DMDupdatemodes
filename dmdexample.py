from dlpcontroller import DLPController
from customexceptions import EnableSWOverrideError, SetSWOverrideValueError
import logging

controller = DLPController()
controller.enable_override()
controller.connect_device()
    