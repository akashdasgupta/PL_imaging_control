# PL imaging control scripts
*Control script for acquiring data using PL imaging setup, publication DOI: [WHEN AVALIABLE]*

*Developer: Akash Dasgupta*

*Scientific contriburers: Suhas Mahesh,Pietro Caprioglio, Yen-Hung Lin, Karl-Augustin Zaininger, Robert D.J. Oliver, Philippe Holzhey, Suer Zhou, Melissa M. McCarthy, Joel A. Smith, Maximilian Frenzel, M. Greyson Christoforo, James M. Ball, Bernard Wenger and Henry J. Snaith*

* For data analysis using script: [LINK WHEN AVALIABLE]
* REQUIRES: ANDOR SDK and pylablib for camera, keithley2600 for smu, pyvisa for power supply of LED

### Equipment

* Camera: ANDOR Zyla 4.2, Kowa LM50XC lens
* SMU: Keithley 
* LED: ThorLabs M450LP1,  powered by Multicomp PRO MP710086
* Mux: Arduino controlled relay switch (Generic amazon one) 

### Usage

* Each piece of equipment has a wrapper class, in a .py file named after the model
* The 'loops' .py file holds many permutations of measurement subroutines that  may be desired

* In a main file, import all the .py files and initialise each equipment class. Set params, and use loops you need.
* Example main files are given: Generic main, main for measuring films, and main for imaging cell at open and short circuit
* The images get saved in the target directory under 'camera', settings dumped in there too
* However SM data is returned, YOU MUST SAVE IT YOURSELF
* Suggested directory structure:
 ```
Root_data_folder    
│
└───Substrate_1
│   └───2  
│       └───oc
│       │   │   LED_power_suply.csv
│       │   │   source_meter.csv
│       │   └───camera
│       │       │     camera_setting_dump.txt
│       │       │     exposure_list.csv
│       │       │     OC_LED=2.580_0.tif
│       │       │     OC_LED=2.580_1.tif
│       │       │     ...
│       └───sc
│       │   │   LED_power_suply.csv
│       │   │   ...
│       └───vsweep   
│       │...
└───Substrate_2
│   │   ...
│    ...
└───white
│   │   ...
```