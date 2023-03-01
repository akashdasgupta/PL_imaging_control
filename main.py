from MulticompPro import *
from AndorZyla import *
from Keithley import *
import csv


with open('Resource_strings.csv','r') as file:
    reader = csv.reader(file)
    string_holder = []
    for row in reader:
        string_holder.append(row[1])

sm_str, led_str, mux_str = string_holder

savepath = r"C:\SCRATCH\test"


cam_exposure_time = 0.01 *2 # s
cam_shutter_mode = 1 # 0 = rolling, 1 = global
cam_bit_depth = 2 # 0 = 12-bit (high well capacity), 1 = 12-bit (low noise), 16-bit (low noise & high well capacity)
num_images = 10 # How many repeats to take

# LED Power supply:
ps_voltage =2.724 # V, for single voltage



#for sweep
ps_vmin = 2.724
ps_vmax = 2.604
ps_vstep = -0.01

#######################################

# Open Device :
Ps = MulticompPro(led_str)
Sm = Keithley(sm_str)
# Mux = AugMux()
Cam = Zyla(cam_exposure_time,cam_bit_depth,cam_shutter_mode)
# Mux.switch_pix(mux_index)

