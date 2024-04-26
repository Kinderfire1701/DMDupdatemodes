from dlpcontroller import *
from customexceptions import EnableSWOverrideError, SetSWOverrideValueError
import logging
import time

controller = DLPControllerActiveX()
controller.connect_device()
print("Is the DMD connected? {}".format(controller.check_device()))
print("Is the connection USB 2.0? {}".format(controller.check_USB_speed()))
print("Is DMD chip version correct (1 for DLP7000)? {}".format(controller.check_DMD_type()))

try:
    print("Image to buffer {}".format(controller.load_image_to_buffer(r"C:\Users\Sid\.venv\updatemodes\DMDupdatemodes\frame_0001.jpg")))
    print("Buffer to DMD {}".format(controller.load_buffer_to_DMD()))
    print("DMD write {}".format(controller.reset())) # writes to DMD state    
    time.sleep(0.05)
    print("DMD cleared {}".format(controller.clear()))
    
except Exception as e:
    print("DMD cleared {}".format(controller.clear()))
    print(e)
    