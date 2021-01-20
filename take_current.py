# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 12:20:49 2020

@author: akashdasgupta
"""

import time
import os
import imageio
import csv
import numpy as np
# Device libs:
from QuickMux_SDK import QuickMux
from keithley2600 import Keithley2600
from pylablib.aux_libs.devices import Andor
import pyvisa as visa

rm = visa.ResourceManager(r'C:\Windows\System32\visa64.dll')
resources = rm.list_resources()
# resource strings:
keithly_string = 'NONE'
power_supply_string = 'NONE'
for resource in resources:
    if resource.startswith("USB"):
        power_supply_string = resource # Only thing that shows up as USB
    elif resource.startswith("GPIB0"): # How it's connected
        keithly_string = resource

# Equipment vars:
cam = None # Camera
k=None # Sourcemeter
#qm=None # Mux
ps =None # Powersupply

# Open Camera:
try:
    cam = Andor.AndorSDK3Camera()
except:
    print("Couldn't connect to ANDOR Zyla!")
    
# !!! Very oddly, camera MUST be opened before mux and sourcemeter, no clue why
# Open sourcemeter: 
try:
    k = Keithley2600(keithly_string, raise_keithley_errors=True, visa_library=r'C:\Windows\System32\visa64.dll') # Keithley Sourcemeter
except:
    print('Could not connect to Keithley sourcemeter! ID given:', keithly_string)

# Open mux:
# try:
#     qm = QuickMux() 
# except:
#     print('Could not connect to QuickMux!')

# Open Power supply
try:
    ps = rm.open_resource(power_supply_string)
    ps.read_termination = '\n'
    ps.write_termination = '\n'
    # Safety: 
    ps.write("OUTPUT OFF")
    ps.write("CURR:LIM 2.01")
except:
    print('Could not connect to LED ower supply! ID given:', keithly_string)

#####################################################################################################
# SETUP, PLEASE EDIT:
#***************************************************  
mux_input_channel = 7
mux_output_channel = 1
    
zyla_exposure_time = 0.001  #s
zyla_shutter_mode = 0 # 0 = rolling, 1 = global#
num_images = 1 # how many repeats

keithly_input_channel = 1 # 0 = A, 1 = B
current_step = 0.01 # amps
    
savepath = r"C:\Users\akashdasgupta\Documents\EL\first_data\test6"
whitepath= savepath+ r"\white"

#*************************************************** 

# Cool the camera:
print("Camera is cooling, please wait...")
cam.set_cooler(True)
while True:
    if float(cam.get_temperature()) <=1:
        break
print("Cooled to 0 deg C")
# We probably don't want any weird noise filtering:
cam.set_value("SpuriousNoiseFilter", False)
cam.set_value("ElectronicShutteringMode", zyla_shutter_mode)
cam.set_exposure(zyla_exposure_time)

# Sets cam to 16 bit: 
cam.set_value("SimplePreAmpGainControl",2) # 0 = 12-bit (high well capacity), 1 = 12-bit (low noise), 16-bit (low noise & high well capacity)

# Sets channel: 
#qm.set_channel(mux_input_channel, mux_output_channel)

if keithly_input_channel:
    kchan = k.smub
else:
    kchan = k.smua

kchan.reset()
kchan.source.output = kchan.OUTPUT_ON
# Not sure if I need this, setting to open circuit:
kchan.source.func = kchan.OUTPUT_DCVOLTS
kchan.source.levelv = 0 
# End of setup
#####################################################################################################

# Functions:

def measure_ps_iv():
    while True:
        try:
            imeas = ps.query("MEAS:CURR?")
            imeas = ps.query("MEAS:CURR?")
            
            imeas = float(imeas)
        except ValueError:
            continue
        break
    return imeas



def int_sweep_oc(vstep, num_snaps, savepath):
    # make directory for backgrounds if not already there:
    if not os.path.isdir(savepath+'\\refs'):
        os.makedirs(savepath+'\\refs')
    
    nominal_voltages = []
    source_currents = []

    image_index = []
    voltage = []
    current = []

    num_refs = 0
    for i in range(10):
        image = cam.snap()
        #]
        imageio.imwrite(savepath+'\\refs'+"\\ref_"+str(num_refs)+".tif", image)
        num_refs += 1

    ps.write("OUTPUT ON")
    for nominal_v in np.arange(2.6, 3.9,vstep):
        ps.write(f"VOLT {nominal_v}")
        time.sleep(2)
        vm = kchan.measure.v()
        im = kchan.measure.i()


        for i in range(num_snaps):
            image = cam.snap()
            imageio.imwrite(savepath + "\\" + str(nominal_v)+"FORWARDS_"+str(i)+".tif", image)
            image_index.append( str(nominal_v)+"FORWARDS_"+str(i)+".tif")
            voltage.append(vm)
            current.append(im)

        ism = measure_ps_iv()

        source_currents.append(ism)
        nominal_voltages.append(nominal_v)
    
    for nominal_v in np.arange(3.9,2.6,-vstep):
        ps.write(f"VOLT {nominal_v}")
        time.sleep(2)
        vm = kchan.measure.v()
        im = kchan.measure.i()

        for i in range(num_snaps):
            image = cam.snap()
            imageio.imwrite(savepath + "\\" + str(nominal_v)+"BACKWARDS"+str(i)+".tif", image)
            image_index.append( str(nominal_v)+"BACKWARDS"+str(i)+".tif")
            voltage.append(vm)
            current.append(im)

        ism = measure_ps_iv()

        source_currents.append(ism)
        nominal_voltages.append(nominal_v)
    
    ps.write("OUTPUT OFF") # for safety
    
    for i in range(10):
        image = cam.snap()
        imageio.imwrite(savepath+'\\refs'+"\\ref_"+str(num_refs)+".tif", image)
        num_refs += 1

    
    with open(savepath+ "\\" + "LED.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(nominal_voltages, source_currents):
            writer.writerow(row)
    
    with open(savepath+ "\\" + "iv.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(image_index, voltage, current):
            writer.writerow(row)

    with open(savepath + "\\" + "camera_setting_dump.txt",'w') as file:
        print(cam.get_all_values(), file=file)

def take_white(whitepath):
    if not os.path.isdir(whitepath):
        os.makedirs(whitepath)
    for i in range(10):
        image = cam.snap()
        imageio.imwrite(whitepath+r"\white_"+str(i)+".tif", image)


int_sweep_oc(current_step,num_images,savepath)
if input("load_white? Y/[N]").lower() == 'Y':
    take_white(whitepath)
# Cleanup: 
# qm.close()
cam.close()
ps.close()