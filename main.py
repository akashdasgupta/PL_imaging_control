from MulticompPro import *
from AndorZyla import *
from Keithley import *
from AugMux import *
from Routines import *
import csv
import atexit

# Define camera configurations, mux index
savepath = r" "
camera_bit_depth = 1 # 0 = 12-bit (packed), 1 = 12-bit, 16-bit 
camera_shutter_mode = 1 # 0 = rolling, 1 = global
mux_index = 4
savepath = f"{savepath}/{mux_index}"

# Appennd your routine parameters here
conditions = []
params = []

conditions.append('oc')
params.append({'savepath':savepath,
               'num_repeats': 10,
               'exposure': 0.05,
               'sm_channel': 'b',
               'led_val': 2.712,
               'ss_time': 10})

intensities = np.arange(2.712,2.602, -0.01)
def exposure_list_maker(exposure):
    if 2.72>= exposure >= 2.652:
        return 0.05
    elif 2.652 > exposure >= 2.622:
        return 0.1
    elif 2.622 > exposure >= 2.602:
        return 1
exposure_list = [exposure_list_maker(i) for i in intensities]
conditions.append('oc_int_dep')
params.append({'savepath':savepath,
               'num_repeats': 3,
               'exposure_list': exposure_list,
               'sm_channel': 'b',
               'led_V_list': intensities,
               'ss_time': 10})

conditions.append('sc')
params.append({'savepath':savepath,
               'num_repeats': 10,
               'exposure': 0.05,
               'sm_channel': 'b',
               'led_val': 2.712,
               'ss_time': 10})


# Parse resource string: 
with open('Resource_strings.csv','r') as file:
    reader = csv.reader(file)
    string_holder = []
    for row in reader:
        string_holder.append(row[1])
sm_str, led_str, mux_str = string_holder

# Open Device :
Ps = MulticompPro(led_str)
Sm = Keithley(sm_str)
Mux = AugMux(mux_str)
Mux.switch_pix(mux_index)
Cam = Zyla(camera_bit_depth,
           camera_shutter_mode)

# Register turning off light and sm on exit
def close_on_exit():
    Ps.off()
    Sm.off()
atexit.register(close_on_exit)  

# Create folder
if not os.path.isdir(savepath):
    os.makedirs(savepath)

# Loop over configured measurements:
for condition, param in zip(conditions, params):
    if condition == 'oc':
        print('Measuring at open circuit')
        measure_open_circuit(Cam,
                             param['savepath'], 
                             param['num_repeats'], 
                             param['exposure'],
                             Sm,
                             param['sm_channel'], 
                             Ps, 
                             param['led_val'],
                             param['ss_time'])
    elif condition == 'sc':
        print('Measuring at short circuit')
        measure_short_circuit(Cam,
                              param['savepath'], 
                              param['num_repeats'], 
                              param['exposure'],
                              Sm,
                              param['sm_channel'], 
                              Ps, 
                              param['led_val'], 
                              param['ss_time'])
    elif condition == 'oc_int_dep':
        print('Measuring Intensity dependant at open circuit')
        measure_intensity_dependant(Cam,
                                    param['savepath'],
                                    param['num_repeats'], 
                                    param['exposure_list'],
                                    Sm,
                                    param['sm_channel'], 
                                    Ps, 
                                    param['led_V_list'], 
                                    param['ss_time'])

    


