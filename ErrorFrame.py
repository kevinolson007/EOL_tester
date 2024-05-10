from PCANBasic import *
import os 
import sys

PcanHandle = PCAN_USBBUS1

Bitrate = PCAN_BAUD_500K

objPCAN = PCANBasic()

result = objPCAN.Initialize(PcanHandle, Bitrate)




def convertString(data):
    strTemp = b""
    for x in data:
        strTemp += b'%.2X ' % x
    return str(strTemp).replace("'","",2).replace("b","",1)




if result != PCAN_ERROR_OK:
    result = objPCAN.GetErrorText(result)
    print(result[1])
else:
    print("PCAN-USB (ch. 1) initialized")


readResult = PCAN_ERROR_OK

while (not(PCAN_ERROR_OK & PCAN_ERROR_QRCVEMPTY)):
    # Check the receive queue for new messages
    #
    readResult = objPCAN.Read(PCAN_USBBUS1)
    if readResult != PCAN_ERROR_QRCVEMPTY and readResult[0] == PCAN_ERROR_OK:
        # Process the received message
        #
        pgn = readResult[1].ID
        data = readResult[1].DATA
        timeStamp = readResult[2]
        print(timeStamp)
        microsTimeStamp = timeStamp.micros + (1000 * timeStamp.millis) + (0x100000000 * 1000 * timeStamp.millis_overflow)
        print(" A message was received")
        print("ID: ",'%.8Xh' %pgn) # Possible processing function, ProcessMessage(msg,timestamp)
        convertedData = convertString(data)
        print("Data: ", convertedData)
        print("Timestamp: ", microsTimeStamp)
        print("================================================")
    else:
        # An error occurred, get a text describing the error and show it
        #
        result = objPCAN.GetErrorText(readResult[0])
        # print(result[1])
        # print(readResult[0]) # Possible errors handling function, HandleError(function_result)

result = objPCAN.Uninitialize(PCAN_USBBUS1)
if result != PCAN_ERROR_OK:
    # An error occurred, get a text describing the error and show it
    #
    result = objPCAN.GetErrorText(result)
    print("Error:", result[1])
else:
    print("PCAN-USB (Ch-1) was released")

