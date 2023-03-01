from pylablib.devices import Andor
import imageio

class Zyla():
    def __init__(self, exposure_time, bit_depth_mode, shutter_mode):
        print("Attempting to connect to ANDOR Zyla...")
        try:
            # Opens Camera:
            self.cam = Andor.AndorSDK3Camera() 
            # We probably don't want any weird noise filtering:
            self.cam.set_attribute_value("SpuriousNoiseFilter", False)
            # Settings:
            self.cam.set_attribute_value("ExposureTime",exposure_time)
            self.cam.set_attribute_value("ElectronicShutteringMode", shutter_mode)
            self.cam.set_attribute_value("SimplePreAmpGainControl",bit_depth_mode) 

            # Wait till camera is cooled upon inti:
            print("Done!\nCamera is cooling, please wait...")
            
            self.cam.set_cooler(True)
            while True:
                if float(self.cam.get_temperature()) <=1: # To 0 deg
                    break
            print("Cooled to 0 deg C")

        except:
            raise IOError("Couldn't initilise ANDOR Zyla!")

    def SetParams(self, exposure=None, shutter_mode=None, bit_depth_mode=None):
        if exposure:
            self.cam.set_attribute_value("ExposureTime",exposure) # in s
        if shutter_mode:
            self.cam.set_attribute_value("ElectronicShutteringMode", shutter_mode) 
            # 0 = rolling, 1 = global
        if bit_depth_mode:
            self.cam.set_attribute_value("SimplePreAmpGainControl",bit_depth_mode) 
            # 0 = 12-bit (high well capacity), 1 = 12-bit (low noise), 16-bit (low noise & high well capacity)
    
    def snap(self, filename):
        image = self.cam.snap() # Saves image to memory
        # Write to disk:
        imageio.imwrite(filename+".tif", image) # tif is the only thing that works!
    
    def dump_settings(self, path):
        with open(path + "\\" + "camera_setting_dump.txt",'w') as file:
            print(self.cam.get_all_values(), file=file) # Saves all parameters to file
    
    def close(self):
        self.cam.close()

# https://pylablib.readthedocs.io/en/latest/.apidoc/pylablib.devices.Andor.html#pylablib.devices.Andor.AndorSDK3.AndorSDK3Camera.get_all_attribute_values

