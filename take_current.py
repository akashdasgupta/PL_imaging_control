# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 12:20:49 2020

@author: akashdasgupta
"""

import time
import imageio
import csv
# Device libs:
from QuickMux_SDK import QuickMux
from keithley2600 import Keithley2600
from pylablib.aux_libs.devices import Andor
import pyvisa as visa

# Open Camera:
try:
    cam = Andor.AndorSDK3Camera()
except:
    print("Couldn't connect to ANDOR Zyla!")
    
# !!! Very oddly, camera MUST be opened before mux and sourcemeter, no clue why

# Open sourcemeter: 
try:
    k = Keithley2600('ASRLCOM1::INSTR',  raise_keithley_errors=True, baud_rate=115200) # Keithley Sourcemeter
except:
    print('Could not connect to Keithley sourcemeter!')

# Open mux:
try:
    qm = QuickMux() 
except:
    print('Could not connect to QuickMux!')

# Open Power supply


#####################################################################################################
# ETC:
    
mux_input_channel = 7
mux_output_channel = 1
    
zyla_exposure_time = 0.1  #s
zyla_shutter_mode = 0 # 0 = rolling, 1 = global

keithly_input_channel = 1 # 0 = A, 1 = B

voltage_min = 2
voltage_max = 3
voltage_step =0.1

led_knotch_levels = [(i+1)/2 for i in range(12)]
led_len = len(led_knotch_levels)
for i in range(led_len):
    led_knotch_levels.append(led_knotch_levels[led_len-i-1])
    
savepath = r"C:\Users\akashdasgupta\Documents\temp"
#####################################################################################################

# Cool the camera:
print("Camera is cooling, please wait...")
cam.set_cooler(True)
while True:
    if float(cam.get_temperature()) <=1:
        break
print("Cooled to 0 deg C")

# Sets cam to 16 bit (bit depth linked to readout speed, its really dumb): 
err = cam.set_value("PixelReadoutRate", 1)# enum, 0= fast (12 bit), 1= normal (16 bit)
# We probably don't want any weird noise filtering:
err  = cam.set_value("SpuriousNoiseFilter", False)
err =  cam.set_value("ElectronicShutteringMode", zyla_shutter_mode)
err = cam.set_exposure(zyla_exposure_time)

# Sets channel: 
qm.set_channel(mux_input_channel, mux_output_channel)

if keithly_input_channel:
    # Reset any Keithly setting: 
    kchan = k.smub
else:
    # Reset any Keithly setting: 
    kchan = k.smua

kchan.reset()
# Not sure if I need this, setting to open circuit:
kchan.source.func = k.smub.OUTPUT_DCVOLTS
kchan.source.levelv = 0 

times = []
voltages = []
currents = []

initime = time.time()
for level in led_knotch_levels:
    input("Set to level: "+str(level)+". Press enter when set.")
    image = cam.snap()
    imageio.imwrite(savepath + "\\" + str(level)+".tif", image)
    
    voltages.append(kchan.measure.v())
    currents.append(kchan.measure.i())
    times.append(time.time()-initime)

with open(savepath+ "\\" + "iv.csv", 'w', newline='') as file:
    writer = csv.writer(file)
    for row in zip(times, voltages, currents):
        writer.writerow(row)

with open(savepath + "\\" + "camera_setting_dump.txt",'w') as file:
    print(cam.get_all_values(), file=file)


# Cleanup: 
qm.close()
cam.close()