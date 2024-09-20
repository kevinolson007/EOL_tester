######################################################################
#  GILLIG END OF LINE TESTING SYSTEM Functions File
#
#  ------------------------------------------------------------------
#  Authors : Shrikrishna Shivakumar and Kevin Olson
#  Company: GILLIG LLC
#  ------------------------------------------------------------------
#
######################################################################

from PCANBasic import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading
import traceback
import sys

import platform

TCL_DONT_WAIT           = 1<<1
TCL_WINDOW_EVENTS       = 1<<2
TCL_FILE_EVENTS         = 1<<3
TCL_TIMER_EVENTS        = 1<<4
TCL_IDLE_EVENTS         = 1<<5
TCL_ALL_EVENTS          = 0

IS_WINDOWS = platform.system() == 'Windows'
DISPLAY_UPDATE_MS = 100

if IS_WINDOWS: 
    FRAME_WIDTH = 760
    FRAME_HEIGHT = 650
    GROUPBOX_WIDTH = 745
    GROUPBOX_HEIGHT = 70
    ENABLE_CAN_FD = True
###*#################################################################################
### Checks if the Windows-Event functionality can be used, by loading               #
### the respective module                                                           #
###                                                                                 #
### Win32 library for Window32 Events handling                                      #
### Module is part of "Python for Win32 Extensions"                                 #
### Web: http://starship.python.net/~skippy/                                        #
##################################################################################### 
    try:
        import win32event
        WINDOWS_EVENT_SUPPORT = True
    except ImportError:     
        WINDOWS_EVENT_SUPPORT = False
else:
    FRAME_WIDTH = 970
    FRAME_HEIGHT = 730
    GROUPBOX_WIDTH = 958
    GROUPBOX_HEIGHT = 80
    ENABLE_CAN_FD = False
    # check driver version before enabling FD
    try: 
        with open("/sys/class/pcan/version") as f:
            version = f.readline()
            if (int(version[0]) >= 8):
                ENABLE_CAN_FD = True
    except Exception:
        ENABLE_CAN_FD = False
    WINDOWS_EVENT_SUPPORT = False

## Convert a CAN DLC value into the actual data length of the CAN/CAN-FD frame.
##
def GetLengthFromDLC(dlc, isSTD):
    if dlc <= 8:
        return dlc
    
    if isSTD :
        return 8
    
    if dlc == 9:
        return 12
    elif dlc == 10:
        return 16
    elif dlc == 11:
        return 20
    elif dlc == 12:
        return 24
    elif dlc == 13:
        return 32
    elif dlc == 14:
        return 48
    elif dlc == 15:
        return 64
    
    return dlc

###*****************************************************************
### Timer class
###*****************************************************************
class TimerRepeater(object):

    """
    A simple timer implementation that repeats itself
    """

    # Constructor
    #
    def __init__(self, name, interval, target, isUi, args=[], kwargs={}):
        """
        Creates a timer.

        Parameters:
            name        name of the thread
            interval    interval in second between execution of target
            target      function that is called every 'interval' seconds
            args        non keyword-argument list for target function
            kwargs      keyword-argument list for target function
        """
        # define thread and stopping thread event
        self._name = name
        self._thread = None
        self._event = None
        self._isUi = isUi
        # initialize target and its arguments
        self._target = target
        self._args = args
        self._kwargs = kwargs
        # initialize timer
        self._interval = interval
        self._bStarted = False

    # Runs the thread that emulates the timer
    #
    def _run(self):
        """
        Runs the thread that emulates the timer.

        Returns:
            None
        """
        while not self._event.wait(self._interval):
            if self._isUi:
                # launch target in the context of the main loop
                window.after(1, self._target,*self._args, **self._kwargs)
            else:
                self._target(*self._args, **self._kwargs)

    # Starts the timer
    #
    def start(self):
        """
        Starts the timer

        Returns:
            None
        """
        # avoid multiple start calls
        if (self._thread == None):
            self._event = threading.Event()
            self._thread = threading.Thread(None, self._run, self._name)
            self._thread.start()

    # Stops the timer
    #
    def stop(self):
        """
        Stops the timer

        Returns:
            None
        """
        if (self._thread != None):
            self._event.set()
            self._thread = None

###*****************************************************************
### Message Status structure used to show CAN Messages
### in a ListView
###*****************************************************************
class MessageStatus(object):
    def __init__(self, canMsg = TPCANMsgFD(), canTimestamp = TPCANTimestampFD(), listIndex = -1):
        self.__m_Msg = canMsg
        self.__m_TimeStamp = canTimestamp
        self.__m_OldTimeStamp = canTimestamp
        self.__m_iIndex = listIndex
        self.__m_iCount = 1
        self.__m_bShowPeriod = True
        self.__m_bWasChanged = False
        self.__m_bWasInserted = True

    def Update(self,canMsg,canTimestamp):
        self.__m_Msg = canMsg
        self.__m_OldTimeStamp = self.__m_TimeStamp
        self.__m_TimeStamp = canTimestamp
        self.__m_bWasChanged = True
        self.__m_iCount = self.__m_iCount + 1      

    @property
    def ShowingPeriod(self):
        return self.__m_bShowPeriod

    @ShowingPeriod.setter
    def ShowingPeriod(self, value):
        if self.__m_bShowPeriod ^ value:
            self.__m_bShowPeriod = value
            self.__m_bWasChanged = True

    @property
    def MarkedAsInserted(self):
        return self.__m_bWasInserted

    @MarkedAsInserted.setter
    def MarkedAsInserted(self, value):
        self.__m_bWasInserted = value
        
    @property
    def MarkedAsUpdated(self):
        return self.__m_bWasChanged

    @MarkedAsUpdated.setter
    def MarkedAsUpdated(self, value):
        self.__m_bWasChanged = value

    @property
    def TypeString(self):        
        isEcho = (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_ECHO.value) == PCAN_MESSAGE_ECHO.value
        
        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_STATUS.value) == PCAN_MESSAGE_STATUS.value:
            return 'STATUS'
        
        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_ERRFRAME.value) == PCAN_MESSAGE_ERRFRAME.value:
            return 'ERROR'        
        
        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            strTemp = 'EXT'
        else:
            strTemp = 'STD'

        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            if (isEcho):
                strTemp += '/RTR [ ECHO ]'
            else:
                strTemp += '/RTR'
        else:
            if (self.__m_Msg.MSGTYPE > PCAN_MESSAGE_EXTENDED.value):
                if (isEcho):
                    strTemp += ' [ECHO'
                else:
                    strTemp += ' ['
                if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_FD.value) == PCAN_MESSAGE_FD.value:
                    strTemp += ' FD'
                if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_BRS.value) == PCAN_MESSAGE_BRS.value:                    
                    strTemp += ' BRS'
                if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_ESI.value) == PCAN_MESSAGE_ESI.value:
                    strTemp += ' ESI'
                strTemp += ' ]'
                
        return strTemp
    
    @property
    def TimeString(self):
        fTime = self.__m_TimeStamp.value / 1000.0
        if self.__m_bShowPeriod:
            fTime -= (self.__m_OldTimeStamp.value / 1000.0)
        return '%.1f' %fTime

    @property
    def IdString(self):
        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            return '%.8X' %self.__m_Msg.ID
        else:
            return '%.3X' %self.__m_Msg.ID

    @property
    def DataString(self):
        strTemp = ''
        if (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            return 'Remote Request'
        else:
            for i in range(GetLengthFromDLC(self.__m_Msg.DLC, not (self.__m_Msg.MSGTYPE & PCAN_MESSAGE_FD.value))):                
                strTemp += '%.2X ' % self.__m_Msg.DATA[i]
        return strTemp

    @property
    def CANMsg(self):
        return self.__m_Msg

    @property
    def Timestamp(self):
        return self.__m_TimeStamp

    @property
    def Position(self):
        return self.__m_iIndex

    @property
    def Count(self):
        return self.__m_iCount


###*****************************************************************