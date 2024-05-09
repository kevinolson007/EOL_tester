from pcan.PCANBasic import *
import time

# region PCAN System Definition
# PCAN Object
objPCAN = PCANBasic()

# Set PCAN to Listen-Only Mode
objPCAN.SetValue(PCAN_USBBUS1,PCAN_LISTEN_ONLY,PCAN_PARAMETER_ON)

# Initializing PCAN USB to Listen to 500K Baud
result = objPCAN.Initialize(PCAN_USBBUS1,PCAN_BAUD_250K)
if result != PCAN_ERROR_OK:
    # An error occurred
    result = objPCAN.GetErrorText(result)
    print (result[1])
else:
    print ("PCAN-USB Was Initialized")

# Set PCAN to Allow Error Frames
objPCAN.SetValue(PCAN_USBBUS1,PCAN_ALLOW_ERROR_FRAMES,PCAN_PARAMETER_OFF)
#endregion

def baud_250_detect():
    init_time = time.monotonic()
    while (time.monotonic() - init_time <= 60):
        can_msg = PCAN_ERROR_OK,
        while((can_msg[0] and PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY):
            can_msg = objPCAN.Read(PCAN_USBBUS1)
            if can_msg[0] != PCAN_ERROR_QRCVEMPTY:
                if (can_msg[1].ID != 2 and can_msg[1].ID != 4 and can_msg[1].ID != 8):
                    return True
    return False

