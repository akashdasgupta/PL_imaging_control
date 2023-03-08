import os
import time
import csv
import numpy as np

def take_bg(cam, campath, start=0):
    if not os.path.isdir(f'{campath}/refs'):
        os.mkdir(f'{campath}/refs')
    for i in range(10):
        cam.snap(f"{campath}/refs/ref_{i+start}")

def measure_point_ss(cam,savepath, num_repeats,sm,sm_channel, sm_bias_type, sm_val, ps, led_val, ss_time):
    # Sets ps state: 
    if sm_bias_type.lower() == 'voltage':
        sm.set_voltage_level(sm_val, sm_channel)
    elif  sm_bias_type.lower() == 'current':
        sm.set_current_level(sm_val, sm_channel)
    else: 
        raise ValueError(f"SM str state must be 'voltage' or 'current', not {sm_val}")
    
    # Turns on illuminationgit diff
    if not led_val == 0:
        ps.set_voltage(led_val)
        ps.on()
    
    # Wait till steady state 
    time.sleep(ss_time) 
    
    # save_string
    if sm_bias_type.lower() == 'current' and sm_val == 0: 
        bias_str = 'OC'
    elif sm_bias_type.lower() == 'voltage' and sm_val == 0:
        bias_str = 'SC'
    elif sm_bias_type.lower() == 'voltage':
        bias_str = f"V={sm_val}"
    save_str = f"{bias_str}_LED={'{:.3f}'.format(led_val)}"  
    
    Vs =[]
    Is = []
    
    # Measure repeats
    for i in range(num_repeats):
        cam.snap(f"{savepath}/camera/{save_str}_{i}") # Dump to disk
        V, I = sm.measure(sm_channel)
        Vs.append(V)
        Is.append(I)
        
    # Return to steady state(oc, dark)
    ps.off()
    sm.set_current_level(0, sm_channel)
    time.sleep(ss_time)
    
    # Returns averafe V/I measured
    return np.mean(Vs), np.mean(Is)
    
def measure_temporal_biasvaried(cam,savepath,sm,sm_channel, sm_bias_types, sm_vals, ps, led_val, wait_between=0):
    init_time = time.time()
    
    # sets initial bias:
    if sm_bias_types[0].lower() == 'voltage':
        sm.set_voltage_level(sm_vals[0], sm_channel)
    elif sm_bias_types[0].lower() == 'current':
        sm.set_current_level(sm_vals[0], sm_channel)
    else: 
        raise ValueError(f"SM str state must be 'voltage' or 'current', not {sm_vals[0]}")

    # Turns on light
    ps.set_voltage(led_val)
    ps.on()
    
    # Give everything time to stabalise a bit:
    time.sleep(1)
    
    Vs =[]
    Is = []
    
    for sm_bias_type, sm_val in zip( sm_bias_types, sm_vals):
        #set bias
        if sm_bias_type.lower() == 'voltage':
            sm.set_voltage_level(sm_val, sm_channel)
        elif sm_bias_type.lower() == 'current':
            sm.set_current_level(sm_val, sm_channel)
        else: 
            raise ValueError(f"SM str state must be 'voltage' or 'current', not {sm_val}")
            
        if sm_bias_type.lower() == 'curent' and sm_val == 0: 
            bias_str = 'OC'
        elif sm_bias_type.lower() == 'voltage' and sm_val == 0:
            bias_str = 'SC'
        elif sm_bias_type.lower() == 'voltage':
            bias_str = f"V={sm_val}"
        elif sm_bias_type.lower() == 'current':
            bias_str = f"I={sm_val}"
            
        save_str = f"{bias_str}_LED={'{:.3f}'.format(led_val)}"
        
        time.sleep(wait_between/2)
        
        cam.snap(f"{savepath}/camera/{save_str}_t={time.time() - init_time}") # Dump to disk
        V, I = sm.measure(sm_channel)
        Vs.append(V)
        Is.append(I)
        
        time.sleep(wait_between/2)
    
    # Return to steady state(oc, dark)
    ps.off()
    sm.set_voltage_level(0, sm_channel)
    time.sleep(wait_between)
    
    # Returns V/I measured
    return np.array(Vs), np.array(Is)
    
def measure_open_circuit(cam,savepath, num_repeats, exposure,sm,sm_channel, ps, led_val, ss_time):
    if not os.path.isdir(f"{savepath}/oc/camera"):
        os.makedirs(f"{savepath}/oc/camera")     
    cam.SetParams(exposure=exposure)
    
    # Bg and measure
    take_bg(cam, f"{savepath}/oc/camera")
    V, I = measure_point_ss(cam,f"{savepath}/oc", num_repeats,sm,sm_channel, 'current', 0, ps, led_val, ss_time)
    take_bg(cam, f"{savepath}/oc/camera")
    
    # save cam settings
    cam.dump_settings(f'{savepath}/oc/camera')
    # save sm readings   
    with open(f"{savepath}/oc/source_meter.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([(V,I)])


def measure_short_circuit(cam,savepath, num_repeats, exposure,sm,sm_channel, ps, led_val, ss_time):
    if not os.path.isdir(f"{savepath}/sc/camera"):
        os.makedirs(f"{savepath}/sc/camera")     
    cam.SetParams(exposure=exposure)
    
    # Bg and measure
    take_bg(cam, f"{savepath}/sc/camera")
    V, I = measure_point_ss(cam,f"{savepath}/sc", num_repeats,sm,sm_channel, 'voltage', 0, ps, led_val, ss_time)
    take_bg(cam,f"{savepath}/sc/camera")
    
    # save cam settings
    cam.dump_settings(f'{savepath}/sc/camera')
    # save sm readings   
    with open(f"{savepath}/sc/source_meter.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([(V,I)])

    
def measure_intensity_dependant(cam,savepath, num_repeats, exposure_list,sm,sm_channel, ps, led_V_list, ss_time):
    if not os.path.isdir(f"{savepath}/oc_int_dep/camera"):
        os.makedirs(f"{savepath}/oc_int_dep/camera")      
    Vs = []
    Is = []
    
    # Bg before
    take_bg(cam,f"{savepath}/oc_int_dep/camera")
    
    # Measure
    for exposure, led_val in zip(exposure_list, led_V_list):
        cam.SetParams(exposure=exposure)
        V, I = measure_point_ss(cam,f"{savepath}/oc_int_dep", num_repeats,sm,sm_channel, 'current', 0, ps, led_val, ss_time)
        Vs.append(V)
        Is.append(I)
    
    # Bg after (end of measure point should return to dark OC)
    take_bg(cam,f"{savepath}/oc_int_dep/camera")
    
    # save cam settings
    cam.dump_settings(f'{savepath}/oc_int_dep/camera')
    # save cam exposure times
    with open(f"{savepath}/oc_int_dep/camera/exposure_list.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in zip(led_V_list, exposure_list):
            writer.writerow(row)
    # save sm readings   
    with open(f"{savepath}/oc_int_dep/source_meter.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([(i,j) for i,j in zip(Vs,Is)])
    # save LED powers used
    with open(f"{savepath}/oc_int_dep/LED_power_supply.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in led_V_list:
            writer.writerow(["{:.3f}".format(float(row))])
            

