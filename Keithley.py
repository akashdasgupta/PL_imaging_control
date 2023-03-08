from keithley2600 import Keithley2600

class Keithley():   
    def __init__(self, keithly_string):
            print("Attempting to connect to the  Keithley sourcemeter...")
            try:
                # Opens device:
                self.sm = Keithley2600(keithly_string, raise_keithley_errors=True,visa_library=r'C:\Windows\System32\visa64.dll')
                # Reset both channels for consistancy:
                self.sm.smua.reset()
                self.sm.smub.reset()
                print("Done!")
            except:
                raise IOError('Could not initilise Keithley sourcemeter!')

    def measure(self, channel='b'):
        """
        Single measurement: just returns voltage and current measured at a channel
        """
        if channel.lower() == 'a':
            v = self.sm.smua.measure.v()
            i = self.sm.smua.measure.i()
            return v,i
        elif channel.lower() == 'b':
            v = self.sm.smub.measure.v()
            i = self.sm.smub.measure.i()
            return v,i

    def set_voltage_level(self, level, channel='b'):  
        if channel.lower() == 'a':
            self.sm.smua.sense = self.sm.smua.SENSE_REMOTE
            self.sm.smua.source.func = self.sm.smua.OUTPUT_DCVOLTS
            self.sm.smua.source.levelv = level 
            self.sm.smua.source.output = self.sm.smua.OUTPUT_ON
        elif channel.lower() == 'b':
            self.sm.smub.sense = self.sm.smub.SENSE_REMOTE
            self.sm.smub.source.func = self.sm.smub.OUTPUT_DCVOLTS
            self.sm.smub.source.levelv = level 
            self.sm.smub.source.output = self.sm.smub.OUTPUT_ON


    def set_current_level(self, level, channel='b'):
        if channel.lower() == 'a':
            self.sm.smua.sense = self.sm.smua.SENSE_REMOTE
            self.sm.smua.source.func = self.sm.smua.OUTPUT_DCAMPS
            self.sm.smua.source.leveli = level 
            self.sm.smua.source.output = self.sm.smua.OUTPUT_ON
        elif channel.lower() == 'b':
            self.sm.smub.sense = self.sm.smub.SENSE_REMOTE
            self.sm.smub.source.func = self.sm.smub.OUTPUT_DCAMPS
            self.sm.smub.source.leveli = level 
            self.sm.smub.source.output = self.sm.smub.OUTPUT_ON
    
    def off(self, channel='b'):
        if channel.lower() == 'a':
            self.sm.smua.source.output = self.sm.smua.OUTPUT_OFF
        elif channel.lower() == 'b':
            self.sm.smub.source.output = self.sm.smub.OUTPUT_OFF