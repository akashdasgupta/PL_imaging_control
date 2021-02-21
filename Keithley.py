import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pyvisa as visa
from keithley2600 import Keithley2600

# We will check if resource manager is open, opens if not, and extracts Keithly resource string:
try:
    rm.list_resources()
except NameError:
    rm = visa.ResourceManager(r'C:\Windows\System32\visa64.dll')
    resources = rm.list_resources()
for resource in resources:
    if resource.startswith("GPIB0"): 
        keithly_string = resource


class Keithley():
    def __init__(self):
            print("Attempting to connect to the  Keithley sourcemeter...")
            try:
                self.sm = Keithley2600(keithly_string, raise_keithley_errors=True, visa_library=r'C:\Windows\System32\visa64.dll')
                sm.smua.reset()
                sm.smub.reset()
                print("Done!")
            except:
                self.sm = None
                print('Could not initilise Keithley sourcemeter! ID given:', keithly_string)
            self.voltages = []
            self.currents = []

        def measure(self, channel='b'):
            if channel == 'a':
                v = self.sm.smua.measure.v()
                i = self.sm.smua.measure.i()
                return v,i
            elif channel == 'b':
                v = self.sm.smub.measure.v()
                i = self.sm.smub.measure.i()
                return v,i
            else:
                print("The provided channel:", channel,"was invalid. Defaulting to b...")
                v = self.sm.smub.measure.v()
                i = self.sm.smub.measure.i()
                return v,i
        
        def set_voltage_level(self, level, channel='b'):
            if channel == 'a':
                self.sm.smua.smua.reset()
                self.sm.smua.source.output = self.sm.source.OUTPUT_ON
                self.sm.smua.source.func = self.sm.source.OUTPUT_DCVOLTS
                self.sm.smua.source.levelv = level 
            elif channel == 'b':
                self.sm.smub.smua.reset()
                self.sm.smub.source.output = self.sm.source.OUTPUT_ON
                self.sm.smub.source.func = self.sm.source.OUTPUT_DCVOLTS
                self.sm.smub.source.levelv = level 
            else:
                print("The provided channel:", channel,"was invalid. Defaulting to b...")
                self.sm.smub.smua.reset()
                self.sm.smub.source.output = self.sm.source.OUTPUT_ON
                self.sm.smub.source.func = self.sm.source.OUTPUT_DCVOLTS
                self.sm.smub.source.levelv = level      

        def set_current_level(self, level, channel='b'):
            if channel == 'a':
                self.sm.smua.smua.reset()
                self.sm.smua.source.output = self.sm.source.OUTPUT_ON
                self.sm.smua.source.func = self.sm.source.OUTPUT_DCAMPS
                self.sm.smua.source.leveli = level 
            elif channel == 'b':
                self.sm.smub.smua.reset()
                self.sm.smub.source.output = self.sm.source.OUTPUT_ON
                self.sm.smub.source.func = self.sm.source.OUTPUT_DCAMPS
                self.sm.smub.source.leveli = level 
            else:
                print("The provided channel:", channel,"was invalid. Defaulting to b...")
                self.sm.smub.smua.reset()
                self.sm.smub.source.output = self.sm.source.OUTPUT_ON
                self.sm.smub.source.func = self.sm.source.OUTPUT_DCAMPS
                self.sm.smub.source.leveli = level    

        def set_sc(self, channel='b'):
            self.set_voltage_level(0,channel)
        def set_oc(self, channel='b'):
            self.set_current_level(0,channel)
        
        def loop_measure(self, channel='b', end=False):
            if end:
                vs = self.voltages
                is = self.currents
                self.voltages = []
                self.currents = []
                return vs, is
            else:
                v,i = self.measure(channel)
                self.voltages.append(v)
                self.currents.append(i)





