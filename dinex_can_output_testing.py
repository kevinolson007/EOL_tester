from Lib.pcan.PCANBasic import *
import time

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

# Ensures that there are 8 bits to every message.
def len_correction(io_list):
    # If the list of bits is less than 8 bits
    if len(io_list) < 8:
        for i in range(len(io_list),8):
            # Add 0s until list of bits has length of 8
            io_list.append(0)
        return io_list
    # If no correction required, return input list
    else:
        return io_list

# Given a module CAN message, dissects CAN message and returns status list [I01,I02,I03,...,I15,I16,O01,O02,...,O15,O16]
# Status = 0 (ON)
# Status = 1 (OFF)
def get_module_list(pcan_msg):
    # Byte 1 contains statuses of O09 to O16. Bit array corrected to ensure length of 8.
    o9o16 = [int(d) for d in str(bin(pcan_msg.DATA[0]))[2:]].reverse()
    o9o16 = len_correction(o9o16)

    # Byte 2 contains statuses of O01 to O08. Bit array corrected to ensure length of 8.
    o1o8 = [int(d) for d in str(bin(pcan_msg.DATA[1]))[2:]].reverse()
    o1o8 = len_correction(o1o8)

    # Byte 3 contains statuses of I09 to I16. Bit array corrected to ensure length of 8.
    i9i16 = [int(d) for d in str(bin(pcan_msg.DATA[2]))[2:]].reverse()
    i9i16 = len_correction(i9i16)

    # Byte 4 contains statuses of I01 to I08. Bit array corrected to ensure length of 8.
    i1i8 = [int(d) for d in str(bin(pcan_msg.DATA[3]))[2:]].reverse()
    i1i8 = len_correction(i1i8)

    return i1i8 + i9i16 + o1o8 + o9o16

# Given a module current message, dissects bytes to obtain current (in mA) for O01 to O08. 
# Returns integer list of length 8 with current values for O01 to O08.
# See get_module_current_2(pcan_msg) for O09 to O13.
def get_module_current_1(pcan_msg):
    out_1_curr = pcan_msg.DATA[0] * 104.0
    out_2_curr = pcan_msg.DATA[1] * 104.0
    out_3_curr = pcan_msg.DATA[2] * 104.0
    out_4_curr = pcan_msg.DATA[3] * 104.0
    out_5_curr = pcan_msg.DATA[4] * 71.2
    out_6_curr = pcan_msg.DATA[5] * 71.2
    out_7_curr = pcan_msg.DATA[6] * 71.2
    out_8_curr = pcan_msg.DATA[7] * 71.2
    return [out_1_curr,out_2_curr,out_3_curr,out_4_curr,out_5_curr,out_6_curr,out_7_curr,out_8_curr]

# Given a module current message, dissects bytes to obtain current (in mA) for O09 to O13. 
# Returns integer list of length 8 with current values for O09 to O13.
# See get_module_current_1(pcan_msg) for O01 to O08.
def get_module_current_2(pcan_msg):
    out_9_curr = pcan_msg.DATA[0] * 71.2
    out_10_curr = pcan_msg.DATA[1] * 71.2
    out_11_curr = pcan_msg.DATA[2] * 71.2
    out_12_curr = pcan_msg.DATA[3] * 71.2
    out_13_curr = pcan_msg.DATA[4] * 71.2
    return [out_9_curr,out_10_curr,out_11_curr,out_12_curr,out_13_curr]

# Test function to obtain module states over CAN. Prints matrix of states for all modules.
def get_module_states():
    # readResult initialized to NO ERROR to enter while loop.
    readResult = (PCAN_ERROR_OK,)
    # PCAN is read so long as there are no critical errors.
    while ((readResult[0] and PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY):
        # Reads each message in the queue
        readResult = dinexPCAN.Read(PCAN_USBBUS1)
        if readResult[0] != PCAN_ERROR_QRCVEMPTY:
            # B1 Module IO
            if (readResult[1].ID == 0x500):
                b1 = get_module_list(readResult[1])
            
            # B2 Module IO
            elif (readResult[1].ID == 0x501):
                b2 = get_module_list(readResult[1])

            # B3 Module IO
            elif (readResult[1].ID == 0x502):
                b3 = get_module_list(readResult[1])

            # B4 Module IO
            elif (readResult[1].ID == 0x503):
                b4 = get_module_list(readResult[1])
                
            # B5 Module IO
            elif (readResult[1].ID == 0x504):
                b5 = get_module_list(readResult[1])
                
            # C1 Module IO
            elif (readResult[1].ID == 0x505):
                c1 = get_module_list(readResult[1])

            # D1 Module IO
            elif (readResult[1].ID == 0x506):
                d1 = get_module_list(readResult[1])

            # D2 Module IO
            elif (readResult[1].ID == 0x507):
                d2 = get_module_list(readResult[1])

            # D3 Module IO
            elif (readResult[1].ID == 0x508):
                d3 = get_module_list(readResult[1])

            else:
                continue
        # Ignore Receive Queue Empty Error. Wait for message.
        elif (readResult[0] == PCAN_ERROR_QRCVEMPTY):
            continue
        # Else, print error message.
        else:
            result = dinexPCAN.GetErrorText(readResult[0])
            print(result[1])
        # Print Matrix
        print([b1,b2,b3,b4,b5,c1,d1,d2,d3])

# Test function to set all B1 outputs to ON. Writes to CAN bus with PCAN object.
def set_B1_all():
    # Initiate CANmsg as a TPCANMsg() structure
    CANmsg = TPCANMsg()
    # CAN ID 0x300 corresponds to B1 Module
    CANmsg.ID = 0x300
    # Set CAN Message Length to 8 Bytes
    CANmsg.LEN = 8
    # Standard CAN Message Type
    CANmsg.MSGTYPE = PCAN_MESSAGE_STANDARD
    # Set first and second byte to 0x00 and all else to Not Available
    for i in range(8):
        if i == 1 or i == 0:
            CANmsg.DATA[i] = 0x00
        else:
            CANmsg.DATA[i] = 0xFF
        pass
    # Write CAN message to Bus
    return dinexPCAN.Write(PCAN_USBBUS1, CANmsg)

# Test function to obtain currents for B1 Module
def get_B1_current():
    # readResult initialized to NO ERROR to enter while loop.
    readResult = (PCAN_ERROR_OK,)
    # PCAN is read so long as there are no critical errors.
    while ((readResult[0] and PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY):
        # Read CAN message in queue
        readResult = dinexPCAN.Read(PCAN_USBBUS1)
        if readResult[0] != PCAN_ERROR_QRCVEMPTY:
            if (readResult[1].ID == 0x580):
                b4_curr_list = get_module_current_1(readResult[1])
                print(b4_curr_list)

# MAIN FUNCTION

previous_time = time.monotonic()
while(True):
    if (time.monotonic() - previous_time > 0.08):
        set_B1_all()
        previous_time = time.monotonic()
    get_B1_current()
    