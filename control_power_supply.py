# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pyvisa as visa
import numpy as np
import csv
import time
from matplotlib import pyplot as plt

rm = visa.ResourceManager(r'C:\Windows\System32\visa64.dll')
resources = rm.list_resources()

# in my PC there's only a GPIB and a USB device connected

for resource in resources:
    if resource.startswith("USB"):
        power_supply_string = resource
    elif resource.startswith("GPIB0"):
        keithly_string = resource

mp = rm.open_resource(power_supply_string)
mp.read_termination = '\n'
mp.write_termination = '\n'
mp.write("OUTPUT OFF")
mp.write("CURR:LIM 2")
# mp.write("VOLT:LIM 3.4")

## TEST 1:   
voltages = np.arange(2.9, 3.4, 0.01)
mp.write("OUTPUT ON")
mp.write("VOLT 2.8")
#time.sleep(10)

mv = []
mi = []

for volt in voltages:
    mp.write(f"volt {volt}")
    v = mp.query("MEAS:VOLT?")
    i = float(mp.query("measure:current?"))
    time.sleep(1)
    mv.append(float(v))
    mi.append(float(i))


mp.write("OUTPUT OFF")
mp.close()

plt.plot(mv, mi)

"""
VOLT?
CURR?
OUTPUT ON
OUTPUT OFF
CURR VALUE (write)
VOLT VALUE (write)
"""