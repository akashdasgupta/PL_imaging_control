import numpy as np
import os
import csv
import imagej
from scipy import ndimage as nd 
from scipy.interpolate import UnivariateSpline
from shutil import copyfile
from PIL import Image
from joblib import Parallel, delayed


# EDIT these : 
datapath = r" "
savepath =  r" "
cropmeasure = 'oc'
measurement_subfolders = ['oc', 'sc', 'oc_int_dep']
alpha = 0.25/0.3087 # Scale factor for area
photodiode_diam = 1.03 # cm, of powermeter, only change upon recalibration 
recrop = True

def find_tif(datapath):
    """ Returns all the tifs in a folder"""
    raw_paths = []
    for _, _, files in os.walk(datapath):
        for file in files:
            if file.endswith(".tif"):  # Only interested in tifs
                raw_paths.append(file)
        break
    return raw_paths

def averager(filenames):
    """Opens and returns average of tiff files"""
    temp = np.array(Image.open(filenames[0]))
    rows, cols = temp.shape
    del temp

    buffer = np.zeros((rows, cols))
    for filename in filenames:
        im = np.array(Image.open(filename), dtype=np.float32) # So there's enough headroom for the uint16
        buffer += im
    average_arr = buffer / len(filenames)
    return average_arr

# Creates lists to loop over
tiff_lists = []
ref_list = []
full_savepaths = []
led_Vs = []
crops = []

# Process savepath
savepath = savepath.replace('\\', '/') # ImageJ can't handel \\ s
if not os.path.isdir(savepath):
    os.makedirs(savepath)

# Import camera pixel calibration
with open(r"../calibration_data/camera_pixel_area.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        pix = float(row[0])
        area = float(row[1])
pixels_per_cm = (pix / area) ** 0.5  # root of pixel area/ known area from cell pic
photodiode_diam_pix = pixels_per_cm * photodiode_diam

# Import LED calibration
nominal_v_cal = []
num_photons = []
with open(r"../calibration_data/ledcal.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        nominal_v_cal.append(float(row[0]))
        num_photons.append(float(row[1]))
# Spline fit LED cal   
LED_spline_fit = UnivariateSpline(nominal_v_cal, np.log(num_photons), k=3, s=0.05)
def ledf(x):
    return np.exp(LED_spline_fit(x))

# Generates dict with folder tree
path_db = {}
for root, dirs, _ in os.walk(datapath):
    for dir in dirs:
        if dir.lower() != "white":
            path_db[dir] = []
            for _, subdirs, _ in os.walk(f"{root}/{dir}"):
                for subdir in subdirs:
                    try:
                        int(subdir)
                        path_db[dir].append(int(subdir))
                    except ValueError:
                        pass
                break
    break
if recrop:
    # ImageJ cropping routine:
    ij = imagej.init(r"C:\Fiji.app", mode='interactive')
    for key in path_db.keys():
        for pix in path_db[key]:
            path = f"{datapath}/{key}/{pix}/{cropmeasure}/camera"
            # Opens image in imageJ and displays:
            dataset = ij.io().open(f"{path}/{find_tif(path)[0]}")
            ij.ui().show(dataset)
            # Wait for user to finish:
            input(f'Crop boundry of {key}, {pix} [Press Enter when done]: ')
            # Log selection and close image
            ij.py.run_macro("""
                            run("Measure");
                            close();
                            """)
    # Same for white center
    whitepath = f"{datapath}/white/camera"
    dataset = ij.io().open(f"{whitepath}/{find_tif(whitepath)[0]}")
    ij.ui().show(dataset)
    input(f'Define enclosing rectangle of beam [Press Enter when done]: ')
    ij.py.run_macro("""
                    run("Measure");
                    close();
                    """)
    # Dump file 
    ij.py.run_macro(f'saveAs("Results", "{savepath}/crop_borders.csv");')

# Load cropped borders: 
crop_db = {}
crop_temp_holder = []
# Dump into a list to start with 
with open(f"{savepath}/crop_borders.csv", 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        _, j_min, i_min, j_width, i_width = [float(k) for k in row]
        # Compute the center of the original rectangle
        i_center = i_min + i_width / 2
        j_center = j_min + j_width / 2

        # Compute the new width and height
        aspect_ratio = j_width / i_width
        new_width = alpha * i_width
        new_height = new_width * aspect_ratio
        
        # Compute the new i_min and j_min values to center the new rectangle at the same location as the original rectangle
        i_min_new = int(i_center - new_width / 2)
        j_min_new = int(j_center - new_height / 2)

        # Adjust the new i_max and j_max values to ensure that the new rectangle has the same aspect ratio as the original rectangle
        i_max_new = int(i_min_new + new_width)
        j_max_new = int(j_min_new + new_height)
        
        crop_temp_holder.append((i_min_new,j_min_new,i_max_new,j_max_new))     

# Catagorise by key, pix: 
for i,key in enumerate(path_db.keys()):
    for j,pix in enumerate(path_db[key]):
        if key in crop_db.keys():
            crop_db[key].append(crop_temp_holder[i+j])
        else:
            crop_db[key] = [crop_temp_holder[i+j]]

# Final row is about white
white_crop_dims = crop_temp_holder[-1]
white_center = (int((white_crop_dims[0]+white_crop_dims[2])/2), int((white_crop_dims[1]+white_crop_dims[3])/2))

# White reference processing:

white_files = find_tif(f"{datapath}/white/camera")
white_ref_files = find_tif(f"{datapath}/white/camera/refs")
# Blurred to remove texture:
white_arr = nd.gaussian_filter(averager([f"{datapath}/white/camera/{i}" for i in  white_files]) - averager([f"{datapath}/white/camera/refs/{i}" for i in white_ref_files]), 20)
# Normalise (So that 1 = average power readout of calibrated powermeter)
pix_in_powermeter = []
for i in range(white_arr.shape[0]):
    for j in range(white_arr.shape[1]):
        if( (i-white_center[0])**2 + (j-white_center[1])**2) <= (photodiode_diam_pix/2)**2:
            pix_in_powermeter.append(white_arr[i,j])
white_norm = white_arr / np.mean(pix_in_powermeter)

for key in path_db.keys():
    for pix_index, pix in enumerate(path_db[key]):
        for measurement_type in measurement_subfolders:
            # Check if measurement type exists for all key/pix
            if not os.path.isdir(f"{datapath}/{key}/{pix}/{measurement_type}"):
                continue

            # Make subfolder:
            if not os.path.isdir(f"{savepath}/{key}/{pix}/{measurement_type}"):
                os.makedirs(f"{savepath}/{key}/{pix}/{measurement_type}")
            
            # Load names of tiffs and refs:
            tiffs_in_folder = find_tif(f"{datapath}/{key}/{pix}/{measurement_type}/camera")
            refs =  find_tif(f"{datapath}/{key}/{pix}/{measurement_type}/camera/refs")
            
            # Load either exposure list or load from camera settings dump:
            if os.path.isfile(f"{datapath}/{key}/{pix}/{measurement_type}/camera/exposure_list.csv"):
                exp_ledpower = []
                exp_exposures = []
                with open(f"{datapath}/{key}/{pix}/{measurement_type}/camera/exposure_list.csv", 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        exp_ledpower.append(float(row[0]))
                        exp_exposures.append(float(row[1]))
            else:
                with open(f"{datapath}/{key}/{pix}/{measurement_type}/camera/camera_setting_dump.txt",'r') as file:
                    exp_ledpower = [None]
                    exp_exposures = [float(file.readlines()[0].split("'ExposureTime':")[1].split(',')[0])]

            # Sort repeats:
            tiff_repeat_db = {}
            for tif_name in tiffs_in_folder:
                sm_output = tif_name.split("_")[0]
                led_v = tif_name.split("_")[1].split("=")[1]
                if f"{sm_output}_{led_v}" in tiff_repeat_db.keys():
                    tiff_repeat_db[f"{sm_output}_{led_v}"].append(tif_name)
                else:
                    tiff_repeat_db[f"{sm_output}_{led_v}"] = [tif_name]
            
            # Final assembly of lists to loop over: 
            for tiff_key in tiff_repeat_db.keys():
                # Data repeats and refs: 
                tiff_lists.append([f"{datapath}/{key}/{pix}/{measurement_type}/camera/{k}" for k in tiff_repeat_db[tiff_key]])
                ref_list.append([f"{datapath}/{key}/{pix}/{measurement_type}/camera/refs/{k}" for k in refs])

                # SM condition for name
                sm_condition = tiff_repeat_db[tiff_key][0].split("_")[0]
                
                # LED powers:
                led_V = tiff_repeat_db[tiff_key][0].split("_")[1].split("=")[1]
                led_Vs.append(float(led_V))

                # Exposures: 
                if len(exp_exposures) == 1:
                    exposure = exp_exposures[0]
                else:
                    exp_index = np.argmin([abs(float(led_V)-i) for i in exp_ledpower])
                    exposure = exp_exposures[exp_index]

                # Savepath wih placeholder for flux calc: 
                full_savepaths.append(f"{savepath}/{key}/{pix}/{measurement_type}/{sm_condition}_FLUX_{exposure}_.npy")  

                # Crop coordinates: 
                crop = crop_db[key][pix_index]
                crops.append(crop)
                
                # Save white params: 
                np.save(f"{savepath}/{key}/{pix}/white", white_arr[crop[0]:crop[2],crop[1]:crop[3]])
                with open(f"{datapath}/white/camera/camera_setting_dump.txt", 'r') as file:
                    white_exposure = float(file.readlines()[0].split("'ExposureTime':")[1].split(',')[0]) #get_cam_exposure(f"{datapath}/white")
                white_nominal_v = white_files[0].split('_')[1].split('=')[1]
                white_flux_scale = ledf(float(white_nominal_v))
                with open(f"{savepath}/white_params.csv", 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Exposure', white_exposure])
                    writer.writerow(['Flux scale', white_flux_scale])
                    
                # Copies data over :
                if os.path.isfile(f"{datapath}/{key}/{pix}/{measurement_type}/source_meter.csv"):
                    copyfile(f"{datapath}/{key}/{pix}/{measurement_type}/source_meter.csv", f"{savepath}/{key}/{pix}/{measurement_type}/source_meter.csv")

                if os.path.isfile(f"{datapath}/{key}/{pix}/{measurement_type}/LED_power_supply.csv"):
                    copyfile(f"{datapath}/{key}/{pix}/{measurement_type}/LED_power_supply.csv", f"{savepath}/{key}/{pix}/{measurement_type}/LED_power_supply.csv")

                if os.path.isfile(f"{datapath}/{key}/{pix}/{measurement_type}/camera/camera_setting_dump.txt"):
                    copyfile(f"{datapath}/{key}/{pix}/{measurement_type}/camera/camera_setting_dump.txt", f"{savepath}/{key}/{pix}/{measurement_type}/camera_setting_dump.txt")

                if os.path.isfile(f"{datapath}/{key}/{pix}/{measurement_type}/camera/exposure_list.csv"):
                    copyfile(f"{datapath}/{key}/{pix}/{measurement_type}/camera/exposure_list.csv", f"{savepath}/{key}/{pix}/{measurement_type}/exposure_list.csv")

    

def process_one_image(tiff_repeat, refs, full_savepath, led_V, crop): # 
# Crop data
imarr_cropped = averager(tiff_repeat)[crop[0]:crop[2],crop[1]:crop[3]] - averager(refs)[crop[0]:crop[2],crop[1]:crop[3]]

# Crop white reference
cropped_white_norm = white_norm[crop[0]:crop[2],crop[1]:crop[3]]

# Calculate how much light fell on the area of the sample:
overall_photon_flux = ledf(led_V)
photon_flux_on_cell = np.mean(cropped_white_norm)*overall_photon_flux

# Fill in flux value in savepath: 
final_savepath = str(photon_flux_on_cell).join(full_savepath.split('FLUX'))

# Whitefield correction : 
final_imarr = (imarr_cropped/cropped_white_norm)*np.mean(cropped_white_norm)

# save
np.save(final_savepath,final_imarr)

# Parallel processs, IO limited so using threading 
Parallel(n_jobs=14, backend='threading')(delayed(process_one_image)(tiff_repeat,
                                                                refs, full_savepath, 
                                                                led_V, 
                                                                crop) for tiff_repeat, refs, full_savepath, led_V, crop in zip(tiff_lists, 
                                                                                                                                ref_list,
                                                                                                                                full_savepaths,
                                                                                                                                led_Vs,
                                                                                                                                crops))

# Manule exit if imageJ interactive open
if recrop:
print('Done! Press ctrl+c to exit')        
