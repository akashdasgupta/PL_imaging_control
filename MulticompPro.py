import pyvisa as visa

class MulticompPro():
    def __init__(self, power_supply_string):
        try:
            print("Attempting to connect to Multicomp power supply...")
            self.ps = visa.ResourceManager().open_resource(power_supply_string)
            self.ps.read_termination = '\n'
            self.ps.write_termination = '\n'
            # Safety: 
            self.ps.write("OUTPUT OFF")
            self.ps.write("CURR:LIM 2.01")
            print("Done!")
        except:
            raise IOError('Could not initilise Multicomp power supply (for LED)!')

    def on(self):
        self.ps.write("OUTPUT ON")
    def off(self):
        self.ps.write("OUTPUT OFF")
    
    def set_voltage(self, value):
        self.ps.write(f"VOLT {value}")
    
    def close(self):
        self.ps.close()
        
    










