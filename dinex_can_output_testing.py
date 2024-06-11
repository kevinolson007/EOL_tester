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

def len_correction(io_list):
    if len(io_list) < 8:
        for i in range(len(io_list),8):
            io_list.append(0)
        return io_list
    else:
        return io_list

def get_module_list(pcan_msg):
    o9o16 = [int(d) for d in str(bin(pcan_msg.DATA[0]))[2:]].reverse()
    o9o16 = len_correction(o9o16)
    o1o8 = [int(d) for d in str(bin(pcan_msg.DATA[1]))[2:]].reverse()
    o1o8 = len_correction(o1o8)
    i9i16 = [int(d) for d in str(bin(pcan_msg.DATA[2]))[2:]].reverse()
    i9i16 = len_correction(i9i16)
    i1i8 = [int(d) for d in str(bin(pcan_msg.DATA[3]))[2:]].reverse()
    i1i8 = len_correction(i1i8)
    return i1i8 + i9i16 + o1o8 + o9o16

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

def get_module_current_2(pcan_msg):
    out_9_curr = pcan_msg.DATA[0] * 71.2
    out_10_curr = pcan_msg.DATA[1] * 71.2
    out_11_curr = pcan_msg.DATA[2] * 71.2
    out_12_curr = pcan_msg.DATA[3] * 71.2
    out_13_curr = pcan_msg.DATA[4] * 71.2
    return [out_9_curr,out_10_curr,out_11_curr,out_12_curr,out_13_curr]

def get_module_states():
    readResult = (PCAN_ERROR_OK,)
    while ((readResult[0] and PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY):
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
                b4 = get_module_list(readResult{1})
                
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

        elif (readResult[0] == PCAN_ERROR_QRCVEMPTY):
            continue
        else:
            result = dinexPCAN.GetErrorText(readResult[0])
            print(result[1])
        print([b1,b2,b3,b4,b5,c1,d1,d2,d3])