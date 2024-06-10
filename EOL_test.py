import time
import can
from can import Message
from can.interface import Bus
import pandas as pd
import csv
import binascii
import os
import psycopg2
from urllib import parse
from hashlib import sha256



#HW Interface
bus = can.Bus(bustype='vector', app_name=None, channel=[0], bitrate=500000, err_reporting = True)           #Vector HW interface
# bus = can.Bus(bustype='pcan', app_name=None, channel='PCAN_USBBUS1', bitrate=500000)     #PCAN HW interface 

# def send_message(): #this is to send messages periodically
    # message = can.Message(arbitration_id = 0x18EAFFF9, data= [218, 254, 0], is_extended_id=True, channel=0)
    # bus.send_periodic(message, .2)
    # print("-----------------------------------------------------")




def send_single_message(message_ID, L_data):

    message = can.Message(arbitration_id = message_ID, data= L_data, is_extended_id=True, channel=0)
    bus.send(message)
    print("------------------------------------------------------")




def receive_TP_message(ctrl_msg_ID, data_msg_ID, msg_rqst, device_name):
    global vehicle_data
    sw_ID = []
    bytes_num = 0
    message_num = 0
    retry_counter = 0
    for msg in bus:
        retry_counter += 1
        str_sw_ID = ""
        data = binascii.hexlify(msg.data)

        if msg.arbitration_id == ctrl_msg_ID and msg_rqst == int(data[10:14], 16):
            bytes_num = int(data[2:4], 16)
            message_num = int(data[6:8], 16)

        elif msg.arbitration_id == data_msg_ID and len(sw_ID) < message_num:
            sw_ID.append(binascii.hexlify(msg.data).decode('ascii'))
        else:
            for x in range(len(sw_ID)):
                for i in range(len(sw_ID[x])):
                    if i == 0 or i == 1:
                        continue
                    elif len(str_sw_ID) < bytes_num * 2:
                        str_sw_ID += str(sw_ID[x][i])

            if len(str_sw_ID) == bytes_num * 2 and bytes_num != 0:
                print(device_name)
                try:
                    decoded_text = bytes.fromhex(str_sw_ID).decode('utf-8', errors='replace')
                    # vehicle_data.append(decoded_text)
                    print(decoded_text)
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError: {e}")
                    vehicle_data.append("Decode Error")
                return decoded_text
                break

        if retry_counter == 10000:
            return "None"
            break
          



def receive_message(ctrl_msg_ID, device_name): #for devices that dont need TP
    global vehicle_data
    sw_ID = []
    retry_counter = 0
    str_sw_ID = ''
    for msg in bus:
        retry_counter += 1
        if msg.arbitration_id == ctrl_msg_ID and len(sw_ID ) < 1:     #this is for the Vanner Equalizer
            print( msg.arbitration_id)

            sw_ID.append(binascii.hexlify(msg.data).decode('ascii'))
            
        if len(sw_ID ) == 1:
            
            # print(new_string1)
            for y in range(len(sw_ID)):
                for m in range(len(sw_ID[y])):
                    if m == 0 or m == 1:                    #remove the first byte of data messages
                        continue
                        # print("here")
                    # elif Equalizer_sw_ID[y][m] == "f" and Equalizer_sw_ID[y][m-1] == 'f': #for some reason 0xff is not decodable
                        # continue
                    else:
                        str_sw_ID += str(sw_ID[y][m])
                        # print("new_string1",new_string1)
            # new_string1 = new_string1[:-2] 
            print(device_name)
            try:
                decoded_text = bytes.fromhex(str_sw_ID).decode('utf-8', errors='replace')
                # vehicle_data.append(decoded_text)
                print(decoded_text)
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError: {e}")
                vehicle_data.append("Decode Error")
            return decoded_text
            break
        if retry_counter == 10000:
            return "None"
            break



def error_check():
    err_counter = 0
    for msg in bus:
        initial_timestamp = msg.timestamp
        break
    print(bus)
    for msg in bus:
        # print("we are in main loop")
        err_frames_sec = (err_counter)/(msg.timestamp-initial_timestamp)
        # print(msg.timestamp)
        # if msg.arbitration_id == 4294967295:    #this is the decimal value for error frame
        #     print("ERROR FOUND")
        #     break
        if msg.is_error_frame:    #there is a field that reports the message type
            print("ERROR FOUND")
            print(msg.is_error_frame)
            print(can.CanError)
            err_counter +=1
            
            # print(msg)
        print(err_frames_sec, "fr/s")
        print("total: ", err_counter)

# Busload Tester for 500K Baud Rate
# j1939_busload(can.Bus() object, int eval_time in seconds)
def j1939_busload(can_bus,evaluation_time):
    # On average there are 145 bits in a J1939 message (incl. stuff bits)
    j1939_avg_bits_per_message = 145
    msg_count = 0
    init_time = time.monotonic()
    # Count Messages for a given amount of time
    while(time.monotonic() - init_time <= evaluation_time):
        for msg in can_bus:
            msg_count += 1
    # Evaluate busload. Busload = (Bits per second / 500000) * 100 %
    rx_bits = j1939_avg_bits_per_message * msg_count
    rx_bits_per_sec = (rx_bits/evaluation_time)
    return (rx_bits_per_sec/500000) * 100



if __name__ == "__main__":
    # main()
    error_check()






