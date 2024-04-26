from dlpcontroller import DLPController
from customexceptions import EnableSWOverrideError, SetSWOverrideValueError
import logging

controller = DLPControllerActiveX()
controller.connect_device()
print("Is the DMD connected? {}".format(controller.check_device()))
print("Is the connection USB 2.0? {}".format(controller.USB_speed()))
print("Is DMD chip version correct (1 for DLP7000)? {}".format(controller.check_DMD_type()))

try:
    pass
except:
    pass
    