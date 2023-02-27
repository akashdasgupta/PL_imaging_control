import pyvisa as visa
import serial.tools.list_ports as sp
import csv

#### Configure your specific setup here: 
resource_strings = {'Keithley Instruments Inc., Model 2636, 1211652, 1.4.2': '', # Keithley ID
                    'FARNELL,MP710086,2017217,FV:V1.5.2': '', # Power supply ID
                    '5&1A1E88E2&0&7':''} # Ardunio serial number


# Checks for scientific equipment
rm = visa.ResourceManager()
terminators = ['\n', ' '] # Does not assume terminator

for rec_str in rm.list_resources():
    # Ignore COM ports that can't be opened: 
    if not rec_str.startswith('ASRL'):
        for term in terminators:
            try:
                temp = rm.open_resource(rec_str)
                temp.read_termination = term
                temp.write_termination = term
                
                device_ID = temp.query('*IDN?')
                if device_ID in resource_strings.keys():
                    resource_strings[device_ID] = rec_str

                break
            except:
                pass

# Checks for ardunio
ports = sp.comports()
for port in ports:
    if port.serial_number in resource_strings.keys():
        resource_strings[port.serial_number] = port.device
        
# Writes strings: 
with open('Resource_strings.csv', 'w', newline='') as csv_file:  
    writer = csv.writer(csv_file)
    for key, (_, value) in zip(['Source_meter', 'LED_power', 'Ardunio_mux'], resource_strings.items()):
       writer.writerow([key, value])
        
