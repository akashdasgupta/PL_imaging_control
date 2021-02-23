#############################################################################
# Function conventions: 

# camera: On=cam1, off=cam2
# Keithley: short circuit = sm1, open circuit = sm2, applied voltage= sm3, 
# #         applied current = sm4, Voltage sweep = sm5
# LED: off = ps1, set_voltage = ps2, sweep = ps3
##############################################################################

from AndorZyla import *
from MulticompPro import *
from Keithley import *
from ArdunioMux import *

import os
import numpy as np

def make_cam_path(savepath):
    if os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')

def cam1sm1ps1(cam,sm, num_images=1, savepath='.', sm_channel='b'):
    """imaging, short circuit, light off"""
    make_cam_path(savepath)
    sm.set_sc(sm_channel)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"SC_LED=0_"+i)
    sm_data = sm.measure(sm_channel)
    return sm_data

def cam1sm1ps2(cam,sm, ps, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, short circuit, light_set at some specified value"""
    sm.set_sc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    for i in range(num_images):
        cam.snap(savepath+'\\'+"SC_LED="+str(led_v)+"_"+i)
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam1sm1ps3(cam,sm, ps, led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, short circuit, light sweeping intensity"""
    sm.set_sc(sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        for i in range(num_images):
            cam.snap(savepath+'\\'+"SC_LED="+str(nominal_v)+"_"+i)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm2ps1(cam,sm, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light off"""
    if os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')
    sm.set_oc(sm_channel)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"OC_LED=0_"+i)
    sm_data = sm.measure(sm_channel)
    return sm_data

def cam1sm2ps2(cam,sm, ps, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light_set at some specified value"""
    sm.set_oc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    for i in range(num_images):
        cam.snap(savepath+'\\'+"OC_LED="+str(led_v)+"_"+i)
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam1sm2ps3(cam,sm, ps,  led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light sweeping intensity"""
    sm.set_oc(sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        for i in range(num_images):
            cam.snap(savepath+'\\'+"OC_LED="+str(nominal_v)+"_"+i)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm3ps1(cam,sm, cell_voltage, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage level, light off"""
    if os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')
    sm.set_voltage_level(cell_voltage, sm_channel)

    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED=0_"+i)
    sm_data = sm.measure(sm_channel)
    return sm_data

def cam1sm3ps2(cam,sm, ps, cell_voltage, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage, light_set at some specified value"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    for i in range(num_images):
        cam.snap(savepath+'\\'+"V="+str(cell_voltage)+"_LED="+str(led_v)+"_"+i)
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam1sm3ps3(cam,sm, ps, cell_voltage, led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage, light sweeping intensity"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        for i in range(num_images):
            cam.snap(savepath+'\\'+"V="+str(cell_voltage)+"_LED="+str(nominal_v)+"_"+i)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm4ps1(cam,sm, cell_current, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light off"""
    if os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')
    sm.set_current_level(cell_current, sm_channel)

    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"I="+str(cell_current)+"_LED=0_"+i)
    sm_data = sm.measure(sm_channel)
    return sm_data

def cam1sm4ps2(cam,sm, ps, cell_current, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light_set at some specified value"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    for i in range(num_images):
        cam.snap(savepath+'\\'+"I="+str(cell_current)+"_LED="+str(led_v)+"_"+i)
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam1sm4ps3(cam,sm, ps, cell_current, led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light sweeping intensity"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        for i in range(num_images):
            cam.snap(savepath+'\\'+"I="+str(cell_current)+"_LED="+str(nominal_v)+"_"+i)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm5ps1(cam,sm, cell_vmin, cell_vmax, cell_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, voltage sweep on cell, light off"""
    if os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')

    for cell_voltage in np.arange(cell_vmin, cell_vmax+cell_vstep, cell_vstep):
        sm.set_voltage_level(cell_voltage, sm_channel)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED=0_"+i)
        sm.loop_measure(sm_channel)
    sm_data = sm.loop_measure(end=True)
    return sm_data

def cam1sm5ps2(cam,sm, ps, cell_vmin, cell_vmax, cell_vstep, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light_set at some specified value"""
    ps.set_voltage(led_v)
    ps.on()
    for cell_voltage in np.arange(cell_vmin, cell_vmax+cell_vstep, cell_vstep):
        sm.set_voltage_level(cell_voltage, sm_channel)
        for i in range(num_images):
            cam.snap(savepath+'\\'+"V="+str(cell_voltage)+"_LED="+str(led_v)+"_"+i)
        sm.loop_measure(sm_channel)
    sm_data = sm.loop_measure(end=True)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam1sm5ps3(*args):
    print("UNSUPPORTED COMBO: Sweeping both the keithley and LED at the same time is currently unsupported!")

def cam0sm1ps1(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm1ps2(sm, ps, led_v, sm_channel='b'):
    """imaging, short circuit, light_set at some specified value"""
    sm.set_sc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm1ps3(sm, ps, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """imaging, short circuit, light sweeping intensity"""
    sm.set_sc(sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm2ps1(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm2ps2(sm, ps, led_v, sm_channel='b'):
    """imaging, open circuit, light_set at some specified value"""
    sm.set_oc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm2ps3(sm, ps,  led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light sweeping intensity"""
    sm.set_oc(sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm3ps1(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm3ps2(sm, ps, cell_voltage, led_v, sm_channel='b'):
    """set voltage, light_set at some specified value"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm3ps3(sm, ps, cell_voltage, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """Set voltage, light sweeping intensity"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm4ps1(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm4ps2(sm, ps, cell_current, led_v, num_images=1, savepath='.', sm_channel='b'):
    """Set current level, light_set at some specified value"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm4ps3(sm, ps, cell_current, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """Set current level, light sweeping intensity"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm5ps1(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm5ps2(sm, ps, cell_vmin, cell_vmax, cell_vstep, led_v, num_images=1, savepath='.', sm_channel='b'):
    """Voltave loop on cell, light_set at some specified value"""
    ps.set_voltage(led_v)
    ps.on()
    for cell_voltage in np.arange(cell_vmin, cell_vmax+cell_vstep, cell_vstep):
        sm.set_voltage_level(cell_voltage, sm_channel)
        sm.loop_measure(sm_channel)
    sm_data = sm.loop_measure(end=True)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm5ps3(*args):
    print("ACTION NOT COMPLETE: Sweeping both the keithley and LED at the same time is currently unsupported!")

