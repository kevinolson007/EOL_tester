######################################################################
#  GILLIG END OF LINE TESTING SYSTEM
#
#  ------------------------------------------------------------------
#  Authors : Shrikrishna Shivakumar and Kevin Olson
#  Company: GILLIG LLC
#  ------------------------------------------------------------------
#
######################################################################

from PCANBasic import *
from pcan_tkinter_functions import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading
import traceback
import sys

import platform

class EOL_tk(object): 
    
    ## Constructor
    ##
    
    def __init__(self, parent):
        # Parent's configuration       
        self.m_Parent = parent
        self.m_Parent.wm_title("End-of-Line Testing System")
        self.m_Parent.protocol("WM_DELETE_WINDOW",self.Form_OnClosing)
        
        # Data to be collected for Database
        self.vehicle_vin = 0
        self.vehicle_pri_can_busload = 0
        self.vehicle_250K_device_detected = False
        self.vehicle_250K_device_SA = 255

        # Frame's configuration
        self.m_Frame = tk.Frame(self.m_Parent)
        self.m_Frame.grid(row=0, column=0, padx=5, pady=2, sticky="nwes")
        
        # CANalysis Tabs Setup (Primary CAN and DINEX CAN Tabs)
        self.can_tab_control = ttk.Notebook(window)
        self.pri_can = ttk.Frame(self.can_tab_control)
        self.dinex_can = ttk.Frame(self.can_tab_control)
        self.e_stroke = ttk.Frame(self.can_tab_control)

        self.can_tab_control.add(self.pri_can, text = "Primary CAN")
        self.can_tab_control.add(self.dinex_can, text = "DINEX CAN")
        self.can_tab_control.add(self.e_stroke, text = "e-Stroke System Test")
        ## ADD NEW TABS HERE IF NEEDED ##


        self.InitializeWindow()
        self.InitializeTabs()
        self.InitializePriCANWidgets()
        self.InitializeDinexCANWidgets()

        #self.SetConnectionStatus(False)

    ## Destructor
    ##
    def destroy (self):
        self.m_Parent.destroy()  

    ## Message loop
    ##
    def loop(self):
        # This is an explict replacement for _tkinter mainloop()
        # It lets catch keyboard interrupts easier, and avoids
        # the 20 msec. dead sleep() which burns a constant CPU.
        while self.exit < 0:
            # There are 2 whiles here. The outer one lets you continue
            # after a ^C interrupt.
            try:
                # This is the replacement for _tkinter mainloop()
                # It blocks waiting for the next Tcl event using select.
                while self.exit < 0:
                    # prevent UI concurrency errors with timers (read and
                    # display)
                    #with self._lock:                    
                    self.m_Parent.tk.dooneevent(TCL_ALL_EVENTS)
            except SystemExit:
                # Tkinter uses SystemExit to exit
                self.exit = 1
                return
            except KeyboardInterrupt:
                if messagebox.askquestion ('Interrupt', 'Really Quit?') == 'yes':
                    # self.tk.eval('exit')
                    self.exit = 1
                    return
                continue
            except:
                # Otherwise it's some other error
                t, v, tb = sys.exc_info()
                text = ""
                for line in traceback.format_exception(t,v,tb):
                    text += line + '\n'
                try: messagebox.showerror ('Error', text)
                except: pass
                self.exit = 1
                raise(SystemExit, 1)
            
    def InitializeWindow(self):
        # title
        self.title_label = tk.Label(master=window, text='EOL Test (Right First Time)', font = 'Helvetica 32 bold')
        window.grid_rowconfigure(0,weight=1)
        window.grid_columnconfigure(0,weight=1)
        self.title_label.grid(row=0,column=0)
        self.exit = -1
        self.m_objPCANBasic = PCANBasic()
        self.m_PcanHandle = PCAN_NONEBUS

    def InitializeTabs(self):
        # Instruction Label ("Select CAN Network to be Analyzed")
        self.instr_label = tk.Label(master=window, text='**Select tab for CAN Network to be Analyzed**', font='Helvetica 12', anchor='w')
        window.grid_rowconfigure(1,weight=1)
        window.grid_columnconfigure(1,weight=1)
        self.instr_label.grid(row=1,column=0, sticky='w')

        #################################################### EOL TEST TABS ##########################################
        
        window.grid_rowconfigure(2,weight=12)
        window.grid_columnconfigure(2,weight=1)
        self.can_tab_control.grid(row=2,column=0,sticky=tk.E+tk.W+tk.N+tk.S,padx=10,pady=10)

        #################################################### TAB GRIDDING ##########################################
        # Arrange Grid in Primary CAN tab
        self.pri_can.rowconfigure(0,weight=1)
        self.pri_can.rowconfigure(1,weight=5)
        self.pri_can.rowconfigure(2,weight=5)
        self.pri_can.rowconfigure(3,weight=3)
        self.pri_can.rowconfigure(4,weight=3)
        self.pri_can.rowconfigure(5,weight=5)
        self.pri_can.columnconfigure(0, weight=2)
        self.pri_can.columnconfigure(1, weight=2)
        self.pri_can.columnconfigure(2,weight=2)

        # Grid Design for Dinex CAN tab
        self.dinex_can.rowconfigure(0,weight=1)
        self.dinex_can.columnconfigure(0,weight=1)

    def InitializePriCANWidgets(self):
        ### ROW 0 ###
        # Tab Title
        self.pri_can_title = tk.Label(self.pri_can, text = 'Primary CAN Checks', font = 'Helvetica 20 bold underline')
        self.pri_can_title.grid(row=0,column=0,columnspan=3,sticky='nsew')

        # Bus VIN Prompt Label
        self.prompt_label = tk.Label(self.pri_can,text='Enter Bus VIN (Last 6): ', font = 'Helvetica 14 bold')
        self.prompt_label.grid(row=1,column=0,padx=5,pady=5,sticky='ns')

        # VIN Entry Validation Registration
        self.validate_vin_wrapper = (self.pri_can.register(self.validate_vin_entry_func), '%P')

        # Bus VIN Entry
        self.bus_vin_input = tk.StringVar()
        self.bus_vin_entry = tk.Entry(self.pri_can,textvariable=self.bus_vin_input,validate='all',validatecommand=self.validate_vin_wrapper)
        self.bus_vin_entry.grid(row=1,column=1,padx=5,pady=5)

        # Bus VIN Submit Button
        self.vin_button = tk.Button(self.pri_can,text='Submit',command=self.vin_button_func,width=10)
        self.vin_button.grid(row=1,column=2,padx=5,pady=5)


        ### ROW 1 ###
        # Busload Label
        self.busload_label = tk.Label(self.pri_can,text='Busload (%): ', font = 'Helvetica 14 bold')
        self.busload_label.grid(row=2,column=0,padx=5,pady=10,sticky='ns')

        # Busload Value Label
        self.busload_value_label_text = tk.StringVar()
        self.busload_value_label_text.set(str(self.vehicle_pri_can_busload) + ' %')
        self.busload_value_label = tk.Label(self.pri_can,textvariable = self.busload_value_label_text, font='Helvetica 14 bold')
        self.busload_value_label.grid(row=2,column=1,padx=5,pady=10,sticky='ns')

        # Busload Calculation Progress Bar
        self.busload_progress_bar = ttk.Progressbar(self.pri_can,mode='indeterminate')

        # Busload Calculate Button
        self.busload_calc_btn = tk.Button(self.pri_can,text='Calculate',width=10,command=self.busload_calc_btn_func)
        self.busload_calc_btn.grid(row=2,column=2,padx=5,pady=10,sticky='ns')

        ### ROW 2 ###
        # 250K Baud Detect Label
        self.can_250_detect_label = tk.Label(self.pri_can,text='250K Baud \nDevice Detection: ', font = 'Helvetica 14 bold')
        self.can_250_detect_label.grid(row=3,column=0,padx=5)

        # 250K Baud Detect Textbox
        self.can_250_text = tk.Text(self.pri_can, wrap='word',width=40,height=10)
        self.can_250_text.grid(row=3,rowspan=2,column=1,columnspan=2,padx=5,pady=10)
        self.can_250_text.insert(tk.END, 'Press START to Begin 250K Baud Device Detection...')
        self.can_250_text.configure(state=tk.DISABLED)

        # 250K Baud Detect Start Button
        self.can_250_btn = tk.Button(self.pri_can,text='START',width=10)
        self.can_250_btn.grid(row=4,column=0)

    def InitializeDinexCANWidgets(self):
        # Title of DINEX CAN Tab
        dinex_can_title = tk.Label(self.dinex_can, text = 'DINEX CAN', font = 'Helvetica 20 bold underline')
        dinex_can_title.grid(row=0,column=0)

    ########################################################## PRI CAN INPUT FUNCTIONS ####################################################
    ### ROW 0 ###
    def validate_vin_entry_func(self, P):
        if len(P) == 0 or (P.isnumeric() and (len(P) <= 6)):
            return True
        else:
            return False

    def vin_button_func(self):
        self.temp_vehicle_vin = self.bus_vin_input.get()
        self.prompt_label.configure(text='Bus VIN Input: ' + self.temp_vehicle_vin)
        vehicle_vin = int(self.temp_vehicle_vin)

    ### ROW 1 ###

    def busload_calc_btn_func(self):
        self.busload_progress_bar.grid(row=2,column=1)
        self.busload_progress_bar.start()
    
        busload_return_disp = tk.StringVar()
        threading.Thread(target=self.busload_calculation, args=(busload_return_disp,)).start()

        self.busload_calc_btn.wait_variable(busload_return_disp)

        self.busload_progress_bar.grid_remove()

        self.vehicle_pri_can_busload = int(busload_return_disp.get())

        self.busload_value_label_text.set(str(self.vehicle_pri_can_busload) + ' %')

    def busload_calculation(self,var):
        start_time = time.monotonic()
        while(time.monotonic()-start_time < 30):
            if ((time.monotonic() - start_time) % 5 == 0):
                print(str(time.monotonic()) + ': 5 seconds elapsed')
            elif (time.monotonic() - start_time >= 25):
                break
            else:
                continue
        var.set('50')

    

    ################################################################################################################################################
    ### Event Handlers
    ################################################################################################################################################

    ## Form-Closing Function / Finish function
    ##
    def Form_OnClosing(self, event=None):
        # Releases the used PCAN-Basic channel
        #
        self.m_objPCANBasic.Uninitialize(self.m_PcanHandle)
        """Quit our mainloop."""
        self.exit = 0

###*****************************************************************
### ROOT
###*****************************************************************       

### Loop-Functionality
def RunMain(window):
    global EOLtest
    # Creating Application
    EOLtest = EOL_tk(window)
    # Application Run / Loop-start
    EOLtest.loop()
    # Application Destruction / Loop-end
    EOLtest.destroy()

if __name__ == '__main__':
    # Create Window to run application
    window = tk.Tk()
    RunMain(window)