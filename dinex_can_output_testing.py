from Lib.pcan.PCANBasic import *

# Create DINEX CAN-specific PCAN Object
dinexPCAN = PCANBasic()

# Set PCAN Parameters for DINEX CAN
result = dinexPCAN.Initialize(PCAN_USBBUS1,PCAN_BAUD_250K)
if result != PCAN_ERROR_OK:
    # An error occurred
    result = dinexPCAN.GetErrorText(result)
    print (result[1])
else:
    print ("PCAN-USB for DINEX Was Initialized")

dinexPCAN.SetValue(PCAN_USBBUS1,PCAN_ALLOW_ERROR_FRAMES,PCAN_PARAMETER_ON)


def get_B4_states():
    readResult = PCAN_ERROR_OK
    while ((readResult[0] and PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY):
        readResult = dinexPCAN.Read(PCAN_USBBUS1)
        if readResult[0] != PCAN_ERROR_QRCVEMPTY:
            if readResult[1].ID == 0x503:
                b4o9o16 = readResult[1].DATA[0]
                b4o1o8 = readResult[1].DATA[1]
                b4i9i16 = readResult[1].DATA[2]
                b4i1i8 = readResult[1].DATA[3]
                print("Byte 1 = " + str(b4o9o16))
                print("Byte 2 = " + str(b4o1o8))
                print("Byte 3 = " + str(b4i9i16))
                print("Byte 4 = " + str(b4i1i8))
            else:
                continue
        else:
            result = dinexPCAN.GetErrorText(readResult[0])
            print(result[1])

if __name__ == "__main__":
    get_B4_states()