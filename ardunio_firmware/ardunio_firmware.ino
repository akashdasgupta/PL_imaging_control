//include all necessary libraries. Dont know which ones at this point
#include <SPI.h>
#include <SD.h>

static int ledPin = 13;
static char actionBrackets[2] = { '<', '>' };
static char queryBrackets[2] = { '?', '?' };
static char panicBrackets[2] = { '!', '!' };

File outputFile;

char tempVariable = 'd';
int tempCount = 0;

const static int numPixels = 6;


typedef struct pixel {
  int SRC_pin;           //which pin on Arduino for each pixel
  int SRC_currentValue;  //HIGH/LOW depending on whether or not activated.
  int SNS_pin;
  int SNS_currentValue;
  int pixelMode;  //either 2 wire or 4 wire, set either 2 or 4 by command from Serial
  //for 2 wire mode, connect only to SRC
};

typedef struct cmd {
  const static int commandLength = 20;
  char fromPython[commandLength + 1] = { '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0' };
  char brackets[2] = { '\0', '\0' };
  String commandString = fromPython;
  int started = 0;
  int finished = 0;
  int type = 0;
  char subsystem[6] = { '\0', '\0', '\0', '\0', '\0', '\0' };
  int location = 0;
  int number = 0;
  int mode = 0;
  int isValid = 0;
  long timeIn = 0;
  long timeOut = 0;
  float returnValue;
  String returnString;
  //Need any other components in the struct?
};


pixel pixels[numPixels];

void configureSystem() {  //define system parameters - which pins on arduino mapped to which SSRs
  //pixel_1_SRC - arduino_D0
  //pixel_1_SNS - arduino_D1
  //pixel_2_SRC - arduino_D6
  //pixel_2_SNS - arduino_D7
  //pixel_3_SRC - arduino_D2
  //pixel_3_SNS - arduino_D3
  //pixel_4_SRC - arduino_D8
  //pixel_4_SNS - arduino_D9
  //pixel_5_SRC - arduino_D4
  //pixel_5_SNS - arduino_D5
  //pixel_6_SRC - arduino_D10
  //pixel_6_SNS - arduino_D11

  int SRC_locations[] = { 0, 6, 2, 8, 4, 10 };  //Locations for SRC activation pins on Arduino, taken from PCB drawing
  int SNS_locations[] = { 1, 7, 3, 9, 5, 11 };  //Locations for SNS activation pins on Arduino, taken from PCB drawing


  for (int i = 0; i <= numPixels; i++) {  //populate array for pixels, set each pixel to off position for SRC and SNS
    pixels[i].SRC_pin = SRC_locations[i];
    pixels[i].SNS_pin = SNS_locations[i];
    pixels[i].SRC_currentValue = LOW;
    pixels[i].SNS_currentValue = LOW;
    pinMode(pixels[i].SRC_pin, OUTPUT);
    pinMode(pixels[i].SNS_pin, OUTPUT);

    digitalWrite(pixels[i].SRC_pin, pixels[i].SRC_currentValue);
    digitalWrite(pixels[i].SNS_pin, pixels[i].SNS_currentValue);
  }
}

cmd readCommand() {
  cmd nullCommand;
  cmd tempCommand;
  tempCommand.started = 0;
  char tempRead = '\0';
  int tempPosition = 0;
  int startBracketFound = 0;
  int endBracketFound = 0;
  tempCommand.isValid = 0;
  //need to add parts that read from serial buffer until a start character is read, then reads until end character is read.
  //if command improperly formatted then the command is invalid. if command.invalid==0 then action is skipped and reply is
  //command is invalid.
  //Serial.println("Enter Command");
  //wait until command is here
  while (Serial.available() < 1) {
    //do nothing but wait
  }
  //read in one single character, check if its a start bracket, then delay 1ms to allow any more stuff to his serial buffer.
  if (Serial.available() > 0) {
    tempRead = Serial.read();
    delay(1);
    if (tempRead == '<' || tempRead == '?' || tempRead == '!') {
      startBracketFound = 1;
      tempCommand.brackets[0] = tempRead;  //for later, check start and end brackets, might just be easier to stick them in their own array
      tempCommand.fromPython[0] = tempRead;
      tempCommand.started = 1;
      tempCommand.timeIn = micros();
      tempPosition = 1;
      //parse commandType
    }
  }
  //if previous char was a bracket, this gets skipped. if not, then script continues to search for start character
  while (Serial.available() > 0 && startBracketFound < 1) {
    tempRead = Serial.read();
    //program continues to read from serial buffer until it finds a start bracket (could be any of the types)
    //maybe think of a better way to this, if tempRead in char* startBracket[];
    if (tempRead == '<' || tempRead == '?' || tempRead == '!') {
      startBracketFound = 1;
      tempCommand.brackets[0] = tempRead;  //for later, check start and end brackets, might just be easier to stick them in their own array
      tempCommand.fromPython[0] = tempRead;
      tempCommand.started = 1;
      tempPosition = 1;
      //parse commandType
    }
  }
  //need a timeout clause in this loop in case command is not long enough and no end bracket is found. Figure this out later
  while (Serial.available() > 0 && endBracketFound == 0 && tempPosition <= tempCommand.commandLength) {
    //read in rest of command until find an end bracket or run out of space in cmd buffer
    //limit max length of command, in case its too long then tempCommand.isValid = 0; escape from process.
    tempRead = Serial.read();
    tempCommand.fromPython[tempPosition] = tempRead;
    if (tempRead == '>' || tempRead == '?' || tempRead == '!') {
      endBracketFound = 1;
      tempCommand.brackets[1] = tempRead;  //escape this loop when end bracket has been read.
    }
    tempPosition++;
  }
  //at this point should now have whole command in char array.

  //some logic here regarding bracketing and parsing command type, depending on type will then parse the rest of the info
  //  if (tempCommand.brackets[0] == '<' && tempCommand.brackets[1] == '>') {
  //    tempCommand.isValid = 1;
  //    tempCommand.type = 1;//action
  //    sscanf(tempCommand.fromPython, "<%03c_%02d_%03d>" , tempCommand.subsystem , &tempCommand.location , &tempCommand.value);
  //  }
  //  else if (tempCommand.brackets[0] == '?' && tempCommand.brackets[1] == '?') {
  //    tempCommand.isValid = 1;
  //    tempCommand.type = 2;//query
  //    sscanf(tempCommand.fromPython, "?%03c_%02d_%03d?" , tempCommand.subsystem , &tempCommand.location , &tempCommand.value);
  //  }
  //  else if (tempCommand.brackets[0] == '!' && tempCommand.brackets[1] == '!') {
  //    tempCommand.isValid = 1;
  //    tempCommand.type = 3;//panic
  //    sscanf(tempCommand.fromPython, "!%03c_%02d_%03d!" , tempCommand.subsystem , &tempCommand.location , &tempCommand.value);
  //  }

  //above code works, trying something new to allow more flexibility in sending commands, so far only can send a subsystem of 3 char long with numbers of any length
  //look into strtok() for parsing command.subsystem of arbitrary length (provided within the limits of command.commandLength = 20)
  //http://www.cplusplus.com/reference/cstring/strtok/
  //should be able to split the input into 3 parts, parse into subsystem, then location, then value. Should be able to do all parts with arbitrary length which will help with error handling.
  if (tempCommand.brackets[0] == '<' && tempCommand.brackets[1] == '>') {
    tempCommand.isValid = 1;
    tempCommand.type = 1;  //action
    sscanf(tempCommand.fromPython, "<%03c_%d_%d>", tempCommand.subsystem, &tempCommand.location, &tempCommand.mode);
    //Serial.println(tempCommand.type);
  } else if (tempCommand.brackets[0] == '?' && tempCommand.brackets[1] == '?') {
    tempCommand.isValid = 1;
    tempCommand.type = 2;  //query
    sscanf(tempCommand.fromPython, "?%03c_%d_%d?", tempCommand.subsystem, &tempCommand.location, &tempCommand.mode);
    //Serial.println(tempCommand.type);
  } else if (tempCommand.brackets[0] == '!' && tempCommand.brackets[1] == '!') {
    tempCommand.isValid = 1;
    tempCommand.type = 3;  //panic
    sscanf(tempCommand.fromPython, "!%03c_%d_%d!", tempCommand.subsystem, &tempCommand.location, &tempCommand.mode);
    //Serial.println(tempCommand.type);
  }

  //Serial.println(tempCommand.fromPython);
  //Serial.println(tempCommand.brackets);
  //Serial.println(tempCommand.type);
  //Serial.println(tempCommand.isValid);
  //parse information from command into the various types.
  //decodes string/array of char that is read in into different parts of command. These then get passed to different functions
  tempCommand.commandString = tempCommand.fromPython;


  //Dunno if I need anything else here
  //Serial.println(F("Read-in Finished"));//for debugging, need to make sure that I get past this stage


  while (Serial.available() > 0) {
    Serial.read();
  }

  //Serial.flush();// flush anything else from the serial buffer? Should be able to not have to do this.

  if (tempCommand.isValid) {
    return tempCommand;
  } else {
    return nullCommand;
  }
}

void selectPixel(int location, int pixelMode) {
  //write LOW to all SSRs - can only have one pixel connected at any one time.
  for (int i = 0; i < numPixels; i++) {
    pixels[i].SRC_currentValue = LOW;
    pixels[i].SNS_currentValue = LOW;

    digitalWrite(pixels[i].SRC_pin, pixels[i].SRC_currentValue);
    digitalWrite(pixels[i].SNS_pin, pixels[i].SNS_currentValue);
  }

  if (location <= numPixels && location > 0) {
    switch (pixelMode) {
      case 2:  //for 2wire mode, only activate SRC, can switch to SNS if more appropriate
        pixels[location - 1].SRC_currentValue = HIGH;
        pixels[location - 1].SNS_currentValue = LOW;
        digitalWrite(pixels[location - 1].SRC_pin, pixels[location - 1].SRC_currentValue);
        digitalWrite(pixels[location - 1].SNS_pin, pixels[location - 1].SNS_currentValue);
        Serial.println("2wire measurement selected");
        break;
      case 4:  //for 4wire mode, activate both SRC and SNS SSRs
        pixels[location - 1].SRC_currentValue = HIGH;
        pixels[location - 1].SNS_currentValue = HIGH;
        digitalWrite(pixels[location - 1].SRC_pin, pixels[location - 1].SRC_currentValue);
        digitalWrite(pixels[location - 1].SNS_pin, pixels[location - 1].SNS_currentValue);
        Serial.println("4wire measurement selected");
        break;
      default:  //In case python sends wrong number in command.
        Serial.println("Something's gone wrong");
        break;
    }
  } else if (location == 100) {
    //write HIGH to all pixels because yolo
    for (int i = 0; i < numPixels; i++) {
      pixels[i].SRC_currentValue = HIGH;
      pixels[i].SNS_currentValue = HIGH;

      digitalWrite(pixels[i].SRC_pin, pixels[i].SRC_currentValue);
      digitalWrite(pixels[i].SNS_pin, pixels[i].SNS_currentValue);
    }
  } else if (location == 0) {
    //write LOW to all pixels to return to idle state
    for (int i = 0; i < numPixels; i++) {
      pixels[i].SRC_currentValue = LOW;
      pixels[i].SNS_currentValue = LOW;

      digitalWrite(pixels[i].SRC_pin, pixels[i].SRC_currentValue);
      digitalWrite(pixels[i].SNS_pin, pixels[i].SNS_currentValue);
    }
  } else {
    delay(10);
  }
}

void panic() {
  //write LOW to all SSRs, isolate all pixels from source meter
  //Serial.println("PANIC");//for debugging
  for (int i = 0; i < numPixels; i++) {
    pixels[i].SRC_currentValue = LOW;
    pixels[i].SNS_currentValue = LOW;

    digitalWrite(pixels[i].SRC_pin, pixels[i].SRC_currentValue);
    digitalWrite(pixels[i].SNS_pin, pixels[i].SNS_currentValue);
  }
  Serial.println("Mr Stark I don't feel so good");
}


void dealWithCommand(cmd inputCommand) {
  //switch statement on type of command.
  //within switch statement if statements based on command.subsystem using strcmp (string compare)
  //directs command wherever it needs to go
  switch (inputCommand.type) {
    case 1:
      if (strcmp(inputCommand.subsystem, "pxl") == 0) {
        selectPixel(inputCommand.location, inputCommand.mode);
      } else {
        Serial.println(F("Still nothing recognised"));
      }
      break;
    case 2:
      if (strcmp(inputCommand.subsystem, "pxl") == 0) {
        delay(1);
        Serial.println("No query function built in yet");  //can query what pixel is connected and in which mode - unused functionality for python GUI
      } else {
        Serial.println(F("Still nothing recognised"));
      }
      break;
    case 3:
      //command type is a panic command
      //writes zero/LOW to *all* analog and digital outputs.
      panic();
      break;
    default:
      Serial.println(F("Unexpected Command Received. Unable to Interpret. Computer Says No"));
  }
  //once everything is done, then respond to python script with some response confirming that command has been received and carried out successfully
}
//define respondCommand() - outputs to python over serial connection.


void respondCommand(cmd inputCommand) {
  //Returns information to python script to ensure that things have actually happened and to make sure the input command has been properly parsed.
  //Information then used in python script to monitor/log state of the system. Probably not useful in MUX code but very important for ALD code
  int debugging = 0;
  // if debugging, spits out way more info to serial port to check everything is being parsed correctly. Otherwise just build response and send it to Python
  //some logic to determine what the response should be. Maybe just repeat the whole command string for now.
  //outputFile.open();
  if (debugging == 1) {
    //  outputFile.println(inputCommand.fromPython);
    //  outputFile.close();
    inputCommand.timeOut = micros();
    //Serial.print(F("inputCommand.fromPython: \t"));
    Serial.println(inputCommand.fromPython);
    //Serial.print(F("inputCommand.subsystem \t"));
    Serial.println(inputCommand.subsystem);
    //Serial.print(F("inputCommand.location: \t"));
    Serial.println(inputCommand.location);
    //Serial.print(F("inputCommand.value: \t"));
    Serial.println(inputCommand.mode);
    //Serial.print(F("inputCommand.type: \t"));
    Serial.println(inputCommand.type);
    long tempDuration = inputCommand.timeOut - inputCommand.timeIn;
    Serial.print(F("Command process Duration on Arduino "));
    Serial.print(tempDuration);
    Serial.println(F(" microseconds"));
  }
  //if not debugging, do the proper thing and send back something to Python script
  else {
    //create ouput string echoing input command format
    // <?! subsystem _ location _ value >?!
    //really only need to do the value part - if its a setting command, just return the input string
    //if its a query command, create new array, only the output number needs to be changed at array indices
    //also need clause here if command.isValid == 0
    if (inputCommand.type == 1) {
      Serial.print("<");
      Serial.print(inputCommand.subsystem);
      Serial.print("_");
      Serial.print(inputCommand.location);
      Serial.print("_");
      //some logic here to tell the function what number to send to python, add if statements to differentiate between the different subsystems
      Serial.print(inputCommand.mode);
      Serial.println(">");

    } else if (inputCommand.type == 2) {

    } else if (inputCommand.type == 3) {
      Serial.println(inputCommand.fromPython);
    }
  }
  inputCommand.timeOut = micros();
  //Serial.print("total elapsed time \t");
  //Serial.println(inputCommand.timeOut - inputCommand.timeIn);
}


void setup() {
  // put your setup code here, to run once:
  configureSystem();

  // put your setup code here, to run once:

  //open serial communications with wait clause - need to wait for comms to be open before proceeding to next step.
  Serial.begin(2000000);
  //some sort of wait clause here that doesnt proceed until the serial connection is made.

  while (Serial.available() == 0) {
    //do nothing but wait for first handshake from python interface, needs to see input from Python or Serial Monitor first before proceeding
  }

  if (Serial.available() > 0) {
    tempVariable = Serial.read();
    delay(10);  //delay for rest of message to hit buffer
    tempCount++;
  }
  while (Serial.available() > 0 && tempCount >= 1 && tempCount < 30) {
    tempVariable = Serial.read();
    tempCount++;
  }
  //flush serial buffer now
  while (Serial.available() > 0) {
    Serial.read();
  }

  Serial.println(F("<START>"));

  //await second handshake where snake lad wants to know how many pixels are allowed, and what measurement modes are allowed

  while (Serial.available() == 0) {
    //do nothing but wait for first handshake from python interface, needs to see input from Python or Serial Monitor first before proceeding
  }
  tempCount = 0;
  if (Serial.available() > 0) {
    tempVariable = Serial.read();
    delay(10);  //delay for rest of message to hit buffer
    tempCount++;
  }
  while (Serial.available() > 0 && tempCount >= 1 && tempCount < 30) {
    tempVariable = Serial.read();
    tempCount++;
  }
  //flush serial buffer now
  while (Serial.available() > 0) {
    Serial.read();
  }

  String secondHandshakeString = "<pxl_6_4>";  //says to snake: 6 pixels and can do 4 wire measurement if requested. By default 4 wire versions can also do 2-wire measurements
  Serial.println(secondHandshakeString);
  //second handshake done, move to main loop to actually use the thing.
}

void loop() {
  // put your main code here, to run repeatedly:

  cmd command;
  //Serial.println("In loop");

  command = readCommand();

  //parse command, have dedicated function
  //parseCommand(command);

  //Deal with whatever the command tells the arduino to do. At the moment it really just needs to echo the command back to Serial
  dealWithCommand(command);

  respondCommand(command);
  //Serial.println(F("Loop finished. Rinse and Repeat"));

  //delay(200);
}