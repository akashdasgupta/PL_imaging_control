# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 12:20:49 2020

@author: akashdasgupta
"""

import time
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
    ps.write("CURR:LIM 2")
except:
    print('Could not connect to LED ower supply! ID given:', keithly_string)

#####################################################################################################
# SETUP, PLEASE EDIT:
#***************************************************  
mux_input_channel = 7
mux_output_channel = 1
    
zyla_exposure_time = 0.1  #s
zyla_shutter_mode = 0 # 0 = rolling, 1 = global

keithly_input_channel = 1 # 0 = A, 1 = B
    
savepath = r"C:\Users\akashdasgupta\Documents\temp"
#*************************************************** 

# Cool the camera:
print("Camera is cooling, please wait...")
cam.set_cooler(True)
while True:
    if float(cam.get_temperature()) <=1:
        break
print("Cooled to 0 deg C")
# Sets cam to 16 bit (bit depth linked to readout speed, its really dumb): 
cam.set_value("PixelReadoutRate", 1)# enum, 0= fast (12 bit), 1= normal (16 bit)
# We probably don't want any weird noise filtering:
cam.set_value("SpuriousNoiseFilter", False)
cam.set_value("ElectronicShutteringMode", zyla_shutter_mode)
cam.set_exposure(zyla_exposure_time)

# Sets channel: 
#qm.set_channel(mux_input_channel, mux_output_channel)

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
# End of setup
#####################################################################################################

# Functions:

def measure_ps_iv():
    while True:
        try:
            vmeas = float(ps.query("MEAS:VOLT?"))
            imeas = float(ps.query("MEAS:CURR?"))
        except ValueError:
            continue
        break
    return imeas, vmeas



def int_sweep_oc(vstep, num_snaps, savepath):
    # Set 0V for open circuit
    kchan.reset()
    kchan.source.func = k.smub.OUTPUT_DCVOLTS
    kchan.source.levelv = 0 

    nominal_voltages = []
    source_voltages = []
    source_currents = []

    image_index = []
    voltage = []
    current = []

    ps.write("OUTPUT ON")
    for nominal_v in np.arange(2.8, 3.85,vstep):
        ps.write(f"VOLT {nominal_v}")
        v1, i1 = measure_ps_iv()

        for i in range(num_snaps):
            vm1 = kchan.measure.v()
            im1 = kchan.measure.i()
            image = cam.snap()
            imageio.imwrite(savepath + "\\" + str(nominal_v)+"FORWARDS_"+str(i)+".tif", image)
            vm2 = kchan.measure.v()
            im2 = kchan.measure.i()
            image_index.append( str(nominal_v)+"FORWARDS_"+str(i)+".tif")
            voltage.append((vm1+vm2)/2)
            current.append((im1+im2)/2)

        v2 ,i2 = measure_ps_iv()

        source_voltages.append((v1+v2)/2)
        source_currents.append((i1+i2)/2)
        nominal_voltages.append(nominal_v)
    
    for nominal_v in np.arange(3.85,2.8,vstep):
        ps.write(f"VOLT {nominal_v}")
        v1 , i1 = measure_ps_iv()

        for i in range(num_snaps):
            vm1 = kchan.measure.v()
            im1 = kchan.measure.i()
            image = cam.snap()
            imageio.imwrite(savepath + "\\" + str(nominal_v)+"BACKWARDS"+str(i)+".tif", image)
            vm2 = kchan.measure.v()
            im2 = kchan.measure.i()
            image_index.append( str(nominal_v)+"BACKWARDS"+str(i)+".tif")
            voltage.append((vm1+vm2)/2)
            current.append((im1+im2)/2)

        v2, i2 = measure_ps_iv()

        source_voltages.append((v1+v2)/2)
        source_currents.append((i1+i2)/2)
        nominal_voltages.append(nominal_v)
    
    ps.write("OUTPUT ON") # for safety
    
    with open(savepath+ "\\" + "LED.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(nominal_voltages, source_voltages, source_currents):
            writer.writerow(row)
    
    with open(savepath+ "\\" + "iv.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(image_index, voltage, current):
            writer.writerow(row)

    with open(savepath + "\\" + "camera_setting_dump.txt",'w') as file:
        print(cam.get_all_values(), file=file)


int_sweep_oc(0.1,2,r"C:\Users\akashdasgupta\Documents\test")

# Cleanup: 
# qm.close()
cam.close()
ps.close()