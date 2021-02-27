from MulticompPro import *
from AndorZyla import *
from Keithley import *
from ArdunioMux import *
from loops import *

import csv

#######################################
# EDIT HERE: 
savepath = r"C:\Users\akashdasgupta\Desktop\new_script_test\material_1\2"
mux_index = 2

# Camera:
cam_exposure_time = 0.1 # s
cam_shutter_mode = 0 # 0 = rolling, 1 = global
cam_bit_depth = 2 # 0 = 12-bit (high well capacity), 1 = 12-bit (low noise), 16-bit (low noise & high well capacity)
num_images = 1 # How many repeats to take

# Source meter:
sm_channel = 'b' # a or b
sm_voltage = 1.0 # (V), For if you use set voltage
sm_current = 0.020 # (A) For if you use set current
# For sweep
sm_vmin = 0
sm_vmax = 1.1
sm_vstep = 0.01

# LED Power supply:
ps_voltage = 2.6 # V, for single voltage
#for sweep
ps_vmin = 2.8
ps_vmax = 2.55
ps_vstep = -0.01

#######################################

# Open Device :
Ps = MulticompPro()
Sm = Keithley()
Mux = ArdunioMux()
Cam = Zyla(cam_exposure_time,cam_bit_depth,cam_shutter_mode)

def exposure_maker(nominal_v):
    if 2.55 <= nominal_v <= 2.6:
        return 10
    elif 2.6 < nominal_v <=2.62:
        return 5
    elif 2.62 < nominal_v <= 2.68:
        return 1
    elif 2.68 < nominal_v <= 2.7:
        return 0.5
    else:
        return 0.1

'''
LOOPS AVALIABLE: 
* Format = cam[index]sm[index]ps[index]
* Indicies are permutation + combination of the following:
    * Camera (cam):
        * 0 = Off
        * 1 = On
    * Source meter (sm):
        * 1 = Short circuit
        * 2 = Open circuit
        * 3 = Apply set voltage
        * 4 = Apply set current
        * 5 = Voltage sweep
    * LED power supply (ps):
        * 0 = ff
        * 1 = Set voltage
        * 2 = Voltage sweep
'''
Mux.switch_pix(mux_index)

print("Taking readings .....")
exposure_list = exposure_maker(np.arange( ps_vmin, ps_vmax+ps_vstep, ps_vstep))
sm_data, ps_data = cam1sm2ps2(Cam, Sm, Ps, ps_vmin, ps_vmax, 
                             ps_vstep,num_images=1, 
                             savepath=savepath,sm_channel='b', exposure_list=exposure_list)

print("Done!\nSaving datafiles ....")

with open(savepath+'\\source_meter.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for row in zip(sm_data[0], sm_data[1]):
        writer.writerow(row)

with open(savepath+'\\LED_power_supply.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for row in ps_data:
        writer.writerow(["{:.3f}".format(float(row))])

print("Done!\nClosing devices...")

Ps.close()
Mux.close()
Cam.close()

print("Done!\nRemember to open box. Make sure LED is off before opening box, just in case!")
