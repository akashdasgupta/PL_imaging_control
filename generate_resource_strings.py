import pyvisa as visa
import serial.tools.list_ports as sp
import csv

#### Configure your specific setup here: 
resource_strings = {'Keithley Instruments Inc., Model 2636, 1211652, 1.4.2': '\n', # Keithley ID
                    'FARNELL,MP710086,2017217,FV:V1.5.2': '\n', # Power supply ID
                    '5&32CF30CB&0&7':' '} # Ardunio serial number


# Checks for scientific equipment
rm = visa.ResourceManager()
resources = rm.list_resources()

for inst_id in resource_strings.keys():
    for rec_str in resources:
        if rec_str.startswith('ASRL'):
            continue

        device = rm.open_resource(rec_str)
        device.read_termination  = resource_strings[inst_id]
        device.write_termination  = resource_strings[inst_id]

        if device.query('*IDN?') == inst_id:
            resource_strings[inst_id] = rec_str
            device.close()
            break
        
        device.close()
   

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
        
