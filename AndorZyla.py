# Stops people from freaking out, but also, plz dont conda update!!:
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from pylablib.aux_libs.devices import Andor
import imageio

class Zyla():
    def __init__(self, exposure_time, bit_depth_mode, shutter_mode):
        print("Attempting to connect to ANDOR Zyla...")
        try:
            self.cam = Andor.AndorSDK3Camera()
            # We probably don't want any weird noise filtering:
            self.cam.set_value("SpuriousNoiseFilter", False)
            self.cam.set_exposure(exposure_time)
            self.cam.set_value("ElectronicShutteringMode", shutter_mode)
            self.cam.set_value("SimplePreAmpGainControl",bit_depth_mode) 

            print("Done!\nCamera is cooling, please wait...")
            self.cam.set_cooler(True)
            while True:
                if float(self.cam.get_temperature()) <=1:
                    break
            print("Cooled to 0 deg C")

        except:
            print("Couldn't initilise ANDOR Zyla!")
            self.cam = None
    def SetParams(self, exposure=None, shutter_mode=None, bit_depth_mode=None):
        if exposure:
            self.cam.set_exposure(exposure) # in s
        if shutter_mode:
            self.cam.set_value("ElectronicShutteringMode", shutter_mode) 
            # 0 = rolling, 1 = global
        if bit_depth_mode:
            self.cam.set_value("SimplePreAmpGainControl",bit_depth_mode) 
            # 0 = 12-bit (high well capacity), 1 = 12-bit (low noise), 16-bit (low noise & high well capacity)
    def snap(self, filename):
        image = self.cam.snap()
        imageio.imwrite(filename+".tif", image) # tif is the only thing that works!
    def close(self):
        self.cam.close()



