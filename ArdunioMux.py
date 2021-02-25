import serial
# Stops people from freaking out, but also, plz dont conda update!!:
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class ArdunioMux():
    fudged_index = [1,2,3,4,5,6]
    def __init__(self):
        try:
            print("Attempting to connect to the Ardunio multiplexer...")
            self.mux = serial.Serial("COM4") # Ardunios usually live in com4
            self.mux.Terminator = ''
            print("Done!")
        except:
            print('Could not initilise the Ardunio multiplexer!')
            self.mux=None
    
    def switch_pix(self, index):
        write_index = self.fudged_index[index+1]
        self.mux.write(str(write_index).encode('UTF-8'))
    
    def close(self):
        self.mux.close()
