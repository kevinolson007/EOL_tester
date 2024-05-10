from PCANBasic imprt *
import os 
import sys

PcanHandle = PCAN_USBBUS1

Bitrate = PCAN_BAUD_500K

IsFD = False

BitrateFD = b'f_clock_mhz=20, nom_brp=5, nom_tseg1=2, nom_tseg2=1, nom_sjw=1, data_brp=2, data_tseg1=3, data_tseg2=1, data_sjw=1'

# m_DLLFound = False

PcanInstance = PCANBasic()


 if IsFD:
    stsResult = PcanInstance.InitializeFD(PcanHandle, BitrateFD)
else:
    stsResult = PcanInstance.Initialize(PcanHandle, Bitrate)
if stsResult != PCAN_ERROR_OK:
    print("Can not initialize. Please check the defines in the code.")

def ReadMessage():
        """
        Function for reading CAN messages on normal CAN devices

        Returns:
            A TPCANStatus error code
        """
        ## We execute the "Read" function of the PCANBasic   
        stsResult = PcanInstance.Read(PcanHandle)

        if stsResult[0] == PCAN_ERROR_OK:
            ## We show the received message
            ProcessMessageCan(stsResult[1],stsResult[2])
            print(stsResult)
            
        return stsResult[0]
def ReadMessages():
    """
    Function for reading PCAN-Basic messages
    """
    stsResult = PCAN_ERROR_OK

    ## We read at least one time the queue looking for messages. If a message is found, we look again trying to 
    ## find more. If the queue is empty or an error occurr, we get out from the dowhile statement.
    while (not (stsResult & PCAN_ERROR_QRCVEMPTY)):
        if IsFD:
            stsResult = ReadMessageFD()
        else:
            stsResult = ReadMessage()
        if stsResult != PCAN_ERROR_OK and stsResult != PCAN_ERROR_QRCVEMPTY:
            ShowStatus(stsResult)
            return

 def ProcessMessageCan(msg,itstimestamp):
         """
         Processes a received CAN message
         
         Parameters:
             msg = The received PCAN-Basic CAN message
             itstimestamp = Timestamp of the message as TPCANTimestamp structure
         """
         microsTimeStamp = itstimestamp.micros + (1000 * itstimestamp.millis) + (0x100000000 * 1000 * itstimestamp.millis_overflow)
         
        #  print("Type: " + GetTypeString(msg.MSGTYPE))
        #  print("ID: " + GetIdString(msg.ID, msg.MSGTYPE))
        #  print("Length: " + str(msg.LEN))
        #  print("Time: " + GetTimeString(microsTimeStamp))
        #  print("Data: " + GetDataString(msg.DATA,msg.MSGTYPE))
         print("----------------------------------------------------------")

ReadMessages()
