from PCANBasic import *
import os 
import sys
import time

PcanHandle = PCAN_USBBUS1

Bitrate = PCAN_BAUD_500K

objPCAN = PCANBasic()

result = objPCAN.Initialize(PcanHandle, Bitrate)




# Global Variables
Total_errors = 0
Bit_error_count = 0
Form_error_count = 0
Stuff_error_count = 0
Other_error_count = 0
x = 0
# Defined by PCAN basic
bit_error = 1
form_error = 2
stuff_error = 4
other_error = 8

# Settings for PCAN 
objPCAN.SetValue(PcanHandle, PCAN_ALLOW_ERROR_FRAMES, PCAN_PARAMETER_ON)
objPCAN.SetValue(PcanHandle, PCAN_LISTEN_ONLY, PCAN_PARAMETER_ON)

#check for errors
if result != PCAN_ERROR_OK:
    result = objPCAN.GetErrorText(result)
    print(result[1])
else:
    print("PCAN-USB (ch. 1) initialized")
    print("Running Error check test. Please wait.....")
    start_time = time.time()    # Get initial time


readResult = PCAN_ERROR_OK




def error_test:
    while (not(PCAN_ERROR_OK & PCAN_ERROR_QRCVEMPTY)):
        # Check the receive queue for new messages
        #
        
        current_time = time.time()
        readResult = objPCAN.Read(PCAN_USBBUS1)
        
        if readResult != PCAN_ERROR_QRCVEMPTY and readResult[0] == PCAN_ERROR_OK:           
            if readResult[1].ID == bit_error:
                Bit_error_count += 1
            elif readResult[1].ID == form_error:
                Form_error_count += 1
            elif readResult[1].ID == stuff_error:
                Stuff_error_count += 1
            elif readResult[1].ID == other_error:
                Other_error_count += 1
            # print("this is the ID", readResult[1].ID)
            if readResult[1].ID == bit_error or readResult[1].ID == form_error or readResult[1].ID == stuff_error or readResult[1].ID == other_error:
                Total_errors +=1
            # pgn = readResult[1].ID
            # data = readResult[1].DATA
            # timeStamp = readResult[2]
            # print(timeStamp)
            # microsTimeStamp = (timeStamp.micros + (1000 * timeStamp.millis) + (0x100000000 * 1000 * timeStamp.millis_overflow))/1000000
            # elapsed_time = microsTimeStamp - initial_time
            elapsed_time = current_time - start_time
            # print("elapsed time: ",elapsed_time)
            # print("A message was received")
            # print("ID: ",'%.8Xh' %pgn) # Change from decimal to hex
            # convertedData = convertString(data)
            # print("Data: ", convertedData)
            # print("Timestamp: ", microsTimeStamp)
            # print(elapsed_time)
            if int(elapsed_time) >= 20:
                print("RESULTS")
                print("================================================")
                if elapsed_time == 0:
                    print("Error Rate (Fr/s): 0")
                else:
                    print("Error Rate (Fr/s): ", Total_errors/elapsed_time)
                print("Total Errors: ", Total_errors)
                print("Bit errors: ", Bit_error_count)
                print("Form Errors: ", Form_error_count)
                print("Stuff Errors: ", Stuff_error_count)
                print("Other Errors; ", Other_error_count)
                print("================================================")
                break

            else:
                continue
        else:
            # An error occurred, get a text describing the error and show it
            #
            result = objPCAN.GetErrorText(readResult[0])
            

    result = objPCAN.Uninitialize(PCAN_USBBUS1)
    if result != PCAN_ERROR_OK:
        # An error occurred, get a text describing the error and show it
        #
        result = objPCAN.GetErrorText(result)
        print("Error:", result[1])


    else:
        print("PCAN-USB (Ch-1) was released")



if __name__ == "__main__":
    error_test()