# from pcan.PCANBasic import *
import tkinter as tk
from tkinter import ttk
import time
import threading

# Data to be collected for Database
vehicle_vin = 0
vehicle_pri_can_busload = 0
vehicle_250K_device_detected = False
vehicle_250K_device_SA = 255

# Create Window
window = tk.Tk()
window.title('EOL Testing System')

# title
title_label = tk.Label(master=window, text='EOL Test (Right First Time)', font = 'Helvetica 32 bold')
window.grid_rowconfigure(0,weight=1)
window.grid_columnconfigure(0,weight=1)
title_label.grid(row=0,column=0)

# Instruction Label ("Select CAN Network to be Analyzed")
instr_label = tk.Label(master=window, text='**Select tab for CAN Network to be Analyzed**', font='Helvetica 12', anchor='w')
window.grid_rowconfigure(1,weight=1)
window.grid_columnconfigure(1,weight=1)
instr_label.grid(row=1,column=0, sticky='w')

# CANalysis Tabs Setup (Primary CAN and DINEX CAN Tabs)
can_tab_control = ttk.Notebook(window)
pri_can = ttk.Frame(can_tab_control)
dinex_can = ttk.Frame(can_tab_control)

can_tab_control.add(pri_can, text = "Primary CAN")
can_tab_control.add(dinex_can, text = "DINEX CAN")
## ADD NEW TABS HERE IF NEEDED ##
window.grid_rowconfigure(2,weight=12)
window.grid_columnconfigure(2,weight=1)
can_tab_control.grid(row=2,column=0,sticky=tk.E+tk.W+tk.N+tk.S,padx=10,pady=10)

########################################################## Tab Gridding Setup ##########################################################

# Arrange Grid in Primary CAN tab
pri_can.rowconfigure(0,weight=1)
pri_can.rowconfigure(1,weight=5)
pri_can.rowconfigure(2,weight=5)
pri_can.rowconfigure(3,weight=3)
pri_can.rowconfigure(4,weight=3)
pri_can.rowconfigure(5,weight=5)
pri_can.columnconfigure(0, weight=2)
pri_can.columnconfigure(1, weight=2)
pri_can.columnconfigure(2,weight=2)


# Grid Design for Dinex CAN tab
dinex_can.rowconfigure(0,weight=1)
dinex_can.columnconfigure(0,weight=1)

########################################################## Primary CAN Input Functions SECTION ##########################################################

### ROW 0 ###
def validate_vin_entry_func(P):
    if len(P) == 0 or (P.isnumeric() and (len(P) <= 6)):
        return True
    else:
        return False
    
vvefcmd = (pri_can.register(validate_vin_entry_func), '%P')

def vin_button_func():
    temp_vehicle_vin = bus_vin_input.get()
    prompt_label.configure(text='Bus VIN Input: ' + temp_vehicle_vin)
    vehicle_vin = int(temp_vehicle_vin)


### ROW 1 ###

def busload_calc_btn_func():
    busload_progress_bar.grid(row=2,column=1)
    busload_progress_bar.start()
    
    busload_return_disp = tk.StringVar()
    threading.Thread(target=busload_calculation, args=(busload_return_disp,)).start()

    busload_calc_btn.wait_variable(busload_return_disp)

    busload_progress_bar.grid_remove()

    vehicle_pri_can_busload = int(busload_return_disp.get())

    busload_value_label_text.set(str(vehicle_pri_can_busload) + ' %')

def busload_calculation(var):
    start_time = time.monotonic()
    while(time.monotonic()-start_time < 30):
        if ((time.monotonic() - start_time) % 5 == 0):
            print(str(time.monotonic()) + ': 5 seconds elapsed')
        elif (time.monotonic() - start_time >= 25):
            break
        else:
            continue
    var.set('50')

########################################################## Primary CAN Widgets SECTION ##########################################################

### ROW 0 ###
# Tab Title
pri_can_title = tk.Label(pri_can, text = 'Primary CAN Checks', font = 'Helvetica 20 bold underline')
pri_can_title.grid(row=0,column=0,columnspan=3,sticky='nsew')

# Bus VIN Prompt Label
prompt_label = tk.Label(pri_can,text='Enter Bus VIN (Last 6): ', font = 'Helvetica 14 bold')
prompt_label.grid(row=1,column=0,padx=5,pady=5,sticky='ns')

# Bus VIN Entry
bus_vin_input = tk.StringVar()
bus_vin_entry = tk.Entry(pri_can,textvariable=bus_vin_input,validate='all',validatecommand=vvefcmd)
bus_vin_entry.grid(row=1,column=1,padx=5,pady=5)

# Bus VIN Submit Button
vin_button = tk.Button(pri_can,text='Submit',command=vin_button_func,width=10)
vin_button.grid(row=1,column=2,padx=5,pady=5)


### ROW 1 ###
# Busload Label
busload_label = tk.Label(pri_can,text='Busload (%): ', font = 'Helvetica 14 bold')
busload_label.grid(row=2,column=0,padx=5,pady=10,sticky='ns')

# Busload Value Label
busload_value_label_text = tk.StringVar()
busload_value_label_text.set(str(vehicle_pri_can_busload) + ' %')
busload_value_label = tk.Label(pri_can,textvariable = busload_value_label_text, font='Helvetica 14 bold')
busload_value_label.grid(row=2,column=1,padx=5,pady=10,sticky='ns')

# Busload Calculation Progress Bar
busload_progress_bar = ttk.Progressbar(pri_can,mode='indeterminate')

# Busload Calculate Button
busload_calc_btn = tk.Button(pri_can,text='Calculate',width=10,command=busload_calc_btn_func)
busload_calc_btn.grid(row=2,column=2,padx=5,pady=10,sticky='ns')

### ROW 2 ###
# 250K Baud Detect Label
can_250_detect_label = tk.Label(pri_can,text='250K Baud \nDevice Detection: ', font = 'Helvetica 14 bold')
can_250_detect_label.grid(row=3,column=0,padx=5)

# 250K Baud Detect Textbox
can_250_text = tk.Text(pri_can, wrap='word',width=40,height=10)
can_250_text.grid(row=3,rowspan=2,column=1,columnspan=2,padx=5,pady=10)
can_250_text.insert(tk.END, 'Press START to Begin 250K Baud Device Detection...')
can_250_text.configure(state=tk.DISABLED)

# 250K Baud Detect Start Button
can_250_btn = tk.Button(pri_can,text='START',width=10)
can_250_btn.grid(row=4,column=0)

########################################################## DINEX CAN Widgets SECTION ##########################################################

# Title of DINEX CAN Tab
dinex_can_title = tk.Label(dinex_can, text = 'DINEX CAN', font = 'Helvetica 20 bold underline')
dinex_can_title.grid(row=0,column=0)


# run
window.mainloop()