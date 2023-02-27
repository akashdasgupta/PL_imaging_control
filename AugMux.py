import serial

class AugMux():
    def __init__(self, COM_port_string):
        try:
            print("Attempting to connect to the Ardunio multiplexer...")
            self.mux = serial.Serial(COM_port_string) # Ardunios usually live in com4
            self.mux.Terminator = ''
            print("Done!")
        except:

            raise IOError('Could not initilise the Ardunio multiplexer! (may blame Aug...)')
    
    def switch_pix(self, index):
        self.mux.write(f"<pxl_{index}_4>".encode('UTF-8')) # command needs to be byte encoded 
    
    def close(self):
        self.mux.close()

if __name__ == "__main__":
    mux = AugMux()
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