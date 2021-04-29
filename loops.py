#############################################################################
# Function conventions: 

# camera: On=cam0, off=cam1
# Keithley: short circuit = sm1, open circuit = sm2, applied voltage= sm3, 
# #         applied current = sm4, Voltage sweep = sm5
# LED: off = ps0, set_voltage = ps1, sweep = ps2
##############################################################################

from AndorZyla import *
from MulticompPro import *
from Keithley import *
from ArdunioMux import *

import os
import time
import csv
import numpy as np

def make_cam_path(savepath):
    if not os.path.isdir(savepath+'\\camera'):
        os.mkdir(savepath+'\\camera')

def take_bg(cam, campath, start=0):
    if not os.path.isdir(campath+'\\refs'):
        os.mkdir(campath+'\\refs')
    for i in range(10):
        cam.snap(campath+f"\\refs\\ref_{i+start}")

def cam1sm1ps0(cam,sm, num_images=1, savepath='.', sm_channel='b'):
    """imaging, short circuit, light off"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_sc(sm_channel)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"SC_LED=0_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data

def cam1sm1ps1(cam,sm, ps, led_v, num_images=1, savepath='.', sm_channel='b', timewait=3):
    """imaging, short circuit, light_set at some specified value"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_sc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    time.sleep(timewait)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"SC_LED="+str(led_v)+"_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data, ps_data

def cam1sm1ps2(cam,sm, ps, led_vmin, led_vmax, led_vstep, num_images=1, exposure_list = None, savepath='.', sm_channel='b',led_constant=0, constant_time=None):
    """imaging, short circuit, light sweeping intensity"""
    if not exposure_list:
        exposure_list = 0.1
        print("Using default exposure, 0.1s")
    
    try:
        is_iter = iter(exposure_list)
    except TypeError:
        exposure_list = [exposure_list for i in range(len(np.arange(led_vmin,led_vmax+led_vstep, led_vstep)))]

    make_cam_path(savepath)
    take_bg(cam, savepath+"\\camera")
    sm.set_sc(sm_channel)
    ps.set_voltage(0)
    if constant_time:
        ps.set_voltage(led_constant)
        ps.on()
        time.sleep(constant_time)
    ps.on()

    ps_data = []
    for k, nominal_v in enumerate(np.arange(led_vmin,led_vmax+led_vstep, led_vstep)):
        ps.set_voltage(nominal_v)
        cam.SetParams(exposure=exposure_list[k])
        time.sleep(3)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"SC_LED="+"{:.3f}".format(nominal_v)+"_"+str(i))
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)
    cam.dump_settings(savepath+'\\camera')
    with open(savepath+'\\camera\\exposure_list.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(np.arange(led_vmin,led_vmax+led_vstep, led_vstep), exposure_list):
            writer.writerow(row)
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm2ps0(cam,sm, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light off"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_oc(sm_channel)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"OC_LED=0_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data

def cam1sm2ps1(cam,sm, ps, led_v, num_images=1, savepath='.', sm_channel='b', timewait=3):
    """imaging, open circuit, light_set at some specified value"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_oc(sm_channel)
    ps.on()
    ps.set_voltage(led_v)
    time.sleep(timewait)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"OC_LED="+str(led_v)+"_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data, ps_data

def cam1sm2ps2(cam,sm, ps,  led_vmin, led_vmax, led_vstep, num_images=1, exposure_list = None, savepath='.', sm_channel='b', led_constant=0, constant_time=None):
    """imaging, open circuit, light sweeping intensity"""
    if not exposure_list:
        exposure_list = 0.1
        print("Using default exposure, 0.1s")
    
    try:
        is_iter = iter(exposure_list)
    except TypeError:
        exposure_list = [exposure_list for i in range(len(np.arange(led_vmin,led_vmax+led_vstep, led_vstep)))]

    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_oc(sm_channel)
    ps.set_voltage(0)
    if constant_time:
        ps.set_voltage(led_constant)
        ps.on()
        time.sleep(constant_time)
    ps.on()

    ps_data = []
    for i, nominal_v in enumerate(np.arange(led_vmin,led_vmax+led_vstep, led_vstep)):
        ps.set_voltage(nominal_v)
        cam.SetParams(exposure=exposure_list[i])
        time.sleep(3)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"OC_LED="+"{:.3f}".format(nominal_v)+"_"+str(i))
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)
    cam.dump_settings(savepath+'\\camera')
    with open(savepath+'\\camera\\exposure_list.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(np.arange(led_vmin,led_vmax+led_vstep, led_vstep), exposure_list):
            writer.writerow(row)
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm3ps0(cam,sm, cell_voltage, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage level, light off"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_voltage_level(cell_voltage, sm_channel)

    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED=0_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    sm.off(sm_channel)
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data

def cam1sm3ps1(cam,sm, ps, cell_voltage, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage, light_set at some specified value"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    time.sleep(3)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED="+str(led_v)+"_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data, ps_data

def cam1sm3ps2(cam,sm, ps, cell_voltage, led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set voltage, light sweeping intensity"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        time.sleep(3)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED="+"{:.3f}".format(nominal_v)+"_"+str(i))
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)
    cam.dump_settings(savepath+'\\camera')

    ps.off()
    sm_data = sm.loop_measure(end=True)
    take_bg(cam, savepath+'\\camera',start=10)

    return sm_data, ps_data

def cam1sm4ps0(cam,sm, cell_current, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light off"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_current_level(cell_current, sm_channel)

    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"I="+str(cell_current)+"_LED=0_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    sm.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data

def cam1sm4ps1(cam,sm, ps, cell_current, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light_set at some specified value"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    time.sleep(3)
    for i in range(num_images):
        cam.snap(savepath+'\\camera\\'+"I="+str(cell_current)+"_LED="+str(led_v)+"_"+str(i))
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data, ps_data

def cam1sm4ps2(cam,sm, ps, cell_current, led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light sweeping intensity"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(0)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        time.sleep(3)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"I="+str(cell_current)+"_LED="+"{:.3f}".format(nominal_v)+"_"+str(i))
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)
    cam.dump_settings(savepath+'\\camera')

    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam1sm5ps0(cam,sm, cell_vmin, cell_vmax, cell_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, voltage sweep on cell, light off"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    for cell_voltage in np.arange(cell_vmin, cell_vmax+cell_vstep, cell_vstep):
        sm.set_voltage_level(cell_voltage, sm_channel)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"V="+str(cell_voltage)+"_LED=0_"+str(i))
        sm.loop_measure(sm_channel)
    cam.dump_settings(savepath+'\\camera')
    sm_data = sm.loop_measure(end=True)
    sm.off(sm_channel)
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data

def cam1sm5ps1(cam,sm, ps, cell_vmin, cell_vmax, cell_vstep, led_v, num_images=1, savepath='.', sm_channel='b'):
    """imaging, set current level, light_set at some specified value"""
    make_cam_path(savepath)
    take_bg(cam, savepath+'\\camera')
    ps.set_voltage(led_v)
    time.sleep(3)
    ps.on()
    for cell_voltage in np.arange(cell_vmin, cell_vmax+cell_vstep, cell_vstep):
        sm.set_voltage_level(cell_voltage, sm_channel)
        for i in range(num_images):
            cam.snap(savepath+'\\camera\\'+"V="+"{:.3f}".format(cell_voltage)+"_LED="+str(led_v)+"_"+str(i))
            #"{:.3f}".format(nominal_v)
        sm.loop_measure(sm_channel)
    cam.dump_settings(savepath+'\\camera')
    sm.off(sm_channel)
    sm_data = sm.loop_measure(end=True)
    ps_data = led_v
    ps.off()
    take_bg(cam, savepath+'\\camera',start=10)
    return sm_data, ps_data

def cam1sm5ps2(*args):
    print("UNSUPPORTED COMBO: Sweeping both the keithley and LED at the same time is currently unsupported!")

def cam0sm1ps0(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm1ps1(sm, ps, led_v, sm_channel='b'):
    """imaging, short circuit, light_set at some specified value"""
    sm.set_sc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    time.sleep(3)
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm1ps2(sm, ps, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """imaging, short circuit, light sweeping intensity"""
    sm.set_sc(sm_channel)
    ps.set_voltage(led_vmin)
    time.sleep(1)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm2ps0(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm2ps1(sm, ps, led_v, sm_channel='b'):
    """imaging, open circuit, light_set at some specified value"""
    sm.set_oc(sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm2ps2(sm, ps,  led_vmin, led_vmax, led_vstep, num_images=1, savepath='.', sm_channel='b'):
    """imaging, open circuit, light sweeping intensity"""
    sm.set_oc(sm_channel)
    ps.set_voltage(led_vmin)
    time.sleep(1)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm3ps0(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm3ps1(sm, ps, cell_voltage, led_v, sm_channel='b'):
    """set voltage, light_set at some specified value"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm3ps2(sm, ps, cell_voltage, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """Set voltage, light sweeping intensity"""
    sm.set_voltage_level(cell_voltage, sm_channel)
    ps.set_voltage(led_vmin)
    time.sleep(1)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm4ps0(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm4ps1(sm, ps, cell_current, led_v, num_images=1, savepath='.', sm_channel='b'):
    """Set current level, light_set at some specified value"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(led_v)
    ps.on()
    sm_data = sm.measure(sm_channel)
    ps_data = led_v
    ps.off()
    return sm_data, ps_data

def cam0sm4ps2(sm, ps, cell_current, led_vmin, led_vmax, led_vstep, sm_channel='b'):
    """Set current level, light sweeping intensity"""
    sm.set_current_level(cell_current, sm_channel)
    ps.set_voltage(led_vmin)
    time.sleep(1)
    ps.on()

    ps_data = []
    for nominal_v in np.arange(led_vmin,led_vmax+led_vstep, led_vstep):
        ps.set_voltage(nominal_v)
        sm.loop_measure(sm_channel)
        ps_data.append(nominal_v)

    ps.off()
    sm_data = sm.loop_measure(end=True)

    return sm_data, ps_data

def cam0sm5ps0(*args):
    print("UNSUPPORTED COMBO: Look this combo is not doing anything...")

def cam0sm5ps1(sm, ps, cell_vmin, cell_vmax, cell_vstep, led_v, num_images=1, savepath='.', sm_channel='b'):
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

def cam0sm5ps2(*args):
    print("ACTION NOT COMPLETE: Sweeping both the keithley and LED at the same time is currently unsupported!")