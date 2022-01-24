import serial
# Stops people from freaking out, but also, plz dont conda update!!:
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class AugMux():
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
        self.mux.write(f"<pxl_{index}_m>".encode('UTF-8')) # command needs to be byte encoded 
    
    def close(self):
        self.mux.close()

if __name__ == "__main__":
    mux = ArdunioMux()
    while True:
        choice = input("Channel (or q to quit): ")
        try:
            mux.switch_pix(int(choice)) 
        except :
            if choice.lower() == 'q':
                mux.close()
                exit()
            else:
                continue