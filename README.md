IonMedicationSystem
===================
The code here is divided into five parts:

1) The main web server is a Django-based application under IonWeb.
To run, use python manage.py runserver

2) The code for the Arduino bodypack is under arduino/BodyPack. The IP address for the main server is hard-coded in.

3) The server code for the dispenser to run is under arduino/DispenserServer. It is built on web.py.
To run, use python main.py 127.0.0.1:8888.
Running on port 8888 is necessary because the dispensing medication page (dispense_medication.html under IonWeb/templates) expects the server to be on port 8888.

4) The dispenser code for the arduino is under arduino/Dispenser. There is an optional _DEBUG flag, that, if set, will cause the arduino to be verbose. The _DEBUG option cannot be used when operating with the dispenser server.

5) The RFID reader is under NFC. 
NFCReader is a class that encapsulates reading the NFC tag.
NFCReaderTyper reads out the data on the RFID tag, enters it on the keyboard, and then presses enter. 
NFCReaderTest prints out the data onto the console. 
NFCTagMemoryDump dumps the memory contents onto the keyboard
BruteForceNFC sends various command APDUs to the tag hoping for a response.

Additional parts:
5) arduino/SerialTerminal tests pyserial communication with the arduino


Dispenser Operation
=======================
The dispenser arduino controller waits for commands via serial. Commands start with an exclamation point.Each command may be followed by one or more parameters. The parameters are given by newline terminating each parameter, e.g. one would type "!dispense\n0\n2\n3" to run the dispense command with parameters 0, 2, and 3.

Currently the supported commands are:
!ping -- to test for successful connection
Parameters:
None

!dispense -- to dispense one or more pills from one or more compartments
Parameters:
1) Zero-indexed compartment to dispense from
2) Number of pills to dispense from, must be > 0 and <= 10 (it is probably an error to dispense more than 10 pills)
3) Weight of the pill; used by the scale to confirm number of pills dispensed

!scale -- to test the operation of the scale
Parameters:
1) Weight of the pill -- The scale will weigh the tray, pause for 5 seconds, reweigh the tray, and calculate the number of pills added during the pause given the weight.

In normal operation, dispense commands are sent from the dispenser to the dispenser server. The dispense operation has three stages: intialization, dispense, and reporting. 

In the initialization phase, the parameters are read in, and the phototransistor is calibrated. Calibration is done by reading the phototransistor value beforehand, and then turning on the laser and rereading the value. The intent is to have code dynamically set the thresholds but for now the values are hardcoded in (see setNoLightThreshold and setLightThreshold). These two thresholds determine when a pill is to be considered to be starting to pass through and to have be completely passed through. When the light threshold is below no_light_threshold, a pill is detected to be passing through the system. The pill is considered to have gone completely passed the system when the light threshold is above light_threshold. The idea behind having two thresholds is that the readings fluctuate over time and so setting a lower no_light_threshold and higher light_threshold gives us more confidence in our measurements.


In the dispense cycle, the tray is first weighed for comparison. Next, the servo is turned on. The servo is not kept on all the time to draw less current and just in case the servo is not centered. Also, we do not want the jitter of the servo to affect the weighing process. The servo is kept on until the phototransistor circuit detects the correct number of pills has fallen through. Then, the servo is reversed a little bit to help prevent the jitter. The phototransitor circuit keeps running during this stage in case a pill drops. Finally, the servo is stopped and pills are weighed by the weighing tray to affirm the phototransistor readings. The weighing tray is ultimate arbiter for the number of pills dispensed. If the required is number has been dispensed, the tray dumps the contents into the cup. If the number in the tray exceeds the desired number, the tray dumps everything into trash, and the whole loop repeats. If the number falls below, the whole loop is repeated (with the desired number of pills being the difference between the number of pills needed to be dispensed and the number of pills in the tray.
