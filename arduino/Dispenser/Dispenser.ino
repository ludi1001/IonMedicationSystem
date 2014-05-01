#include <Servo.h>

#define NUM_COMPARTMENTS       6  //number of compartments
#define MAX_PILLS              10 //maximum number of pills to dispense
#define MAX_PILL_WEIGHT        1000 //max pill weight in mg
#define MAX_WAITING_TIME       10000 //max time (in milliseconds) to wait for pill to dispense before concluding it is empty 
#define MG_PER_MV              2 //mg per mv for tray
#define NUM_PHOTO_SAMPLES      1 //number of samples to take for phototransistor readings
#define BLOCKED_LASER_THRESH   10 //threshold for blocked laser
#define UNBLOCKED_LASER_THRESH 80 //threshold for laser to be considered unblocked
#define SERVO_FORWARD          88 //value to send to servo to move it forward
#define SERVO_BACKWARD         91 //value to send to servo to move it backward
#define SERVO_STOP             90 //value to send to servo to stop it
#define SERVO_REVERSE_TIME     750000 //time to reverse servo after each dispense

#define PIN_TRAY_SERVO 1
#define PIN_TRAY       A0

//#define _DEBUG

#ifdef _DEBUG
#define DEBUG_OUT(x) Serial.println(x);
#else
#define DEBUG_OUT(x) ;
#endif

/**************************************/
struct Compartment {
  int diode;
  int detector;
  int servo;
};

Compartment compartments[NUM_COMPARTMENTS];
/**************************************/
void setup() {
  Serial.begin(9600);
  Serial.setTimeout(5000);
  
  pinMode(PIN_TRAY, INPUT);
  
  setupCompartments();
  for(int i = 0; i < NUM_COMPARTMENTS; ++i) {
    pinMode(compartments[i].diode, OUTPUT);
    pinMode(compartments[i].detector, INPUT);
  }
}

void setupCompartments() {
  compartments[0].diode = 3;
  compartments[0].servo = 7;
  compartments[0].detector = A1;
}

void loop() {
  if(Serial.available()) {
    char buffer[100];
    for(int i = 0; i < 100; ++i) buffer[i] = 0;
    
    int res = Serial.readBytesUntil('\n', buffer, 100); 
    char first_char = buffer[0];
    if(res <= 0) return; //make sure we read nonzero data
   
    if(first_char == '!') { //a command was sent
      if(strcmp(buffer+1, "ping") == 0)
        ping();
      else if(strcmp(buffer+1, "dispense") == 0)
        dispense();
      else if(strcmp(buffer+1, "scale") == 0)
        scale();
    }
    else {
      //Serial.println(buffer); //echo back
    }
  }
}
/**************************************/
void ping() {
  Serial.println("ping successful");
}
void scale() {
  int weight = Serial.parseInt();
  Serial.println(weight);
  Serial.println("Weighing...");
  int before = weighTray();
  Serial.println(before);
  Serial.println("Pause");
  delay(5000);
  Serial.println("Weighing...");
  int after = weighTray();
  Serial.println(after);
  Serial.println(calculatePillsDispensed(before, after, weight));
}
void dispense() {
   //check that cup is present
   if(!isCupPresent()) {
     Serial.println("!nocup");
     return;
   }
   
   //grab the dispenser number
   int index = Serial.parseInt();
   //make sure dispenser index is valid
   if(index < 0 || index >= NUM_COMPARTMENTS) {
     Serial.println("!error");
     Serial.println("Illegal compartment number");
     return;
   }

   //grab number of pills to dispense
   int num_pills = Serial.parseInt();
   if(num_pills <= 0 || num_pills >= MAX_PILLS) {
     Serial.println("!error");
     Serial.println("Invalid number of pills requested");
     return;
   }

   //get pill weight
   int pill_weight = Serial.parseInt();
   if(pill_weight <= 0 || pill_weight >= MAX_PILL_WEIGHT) {
     Serial.println("!error");
     Serial.println("Invalid pill weight");
   }
   
   /****TODO*/
   Serial.println("!successful_dispense");
   Serial.println(3);
  /* return;

   DEBUG_OUT("Setting up phototransistor...");
   #ifdef _DEBUG
   delay(2000);
   #endif
   //read ambient noise for phototransistor
   setNoLightThreshold(compartments[index].detector);

   //turn laser diode on
   digitalWrite(compartments[index].diode, HIGH);
   
   //read phototransistor value
   setLightThreshold(compartments[index].detector);
   
   int pills_in_tray = 0; //pills dispensed for patient in tray
   int total_pills_dispensed = 0; //pills dispensed in total, including those trashed
   
   DEBUG_OUT("Starting to dispense...");
   Servo servo;
   
   //run until we have desired number of pills as verified by scale
   while(pills_in_tray < num_pills) {
     //weight tray beforehand
     int tray_before = weighTray();
     
     DEBUG_OUT("Turning servo on...");
     
     //turn servo on
     servo.attach(compartments[index].servo);
     
     unsigned long start_time = micros();
     
     int pills_dispensed = 0; //counter for loop
     //keep running until we have the desired number of pills as detected by phototransistor
     while(pills_dispensed < num_pills - pills_in_tray) {
       servo.write(SERVO_FORWARD);
       //keep running until we hit a pill
       while(!checkPhototransistor(compartments[index].detector)) {     
         //if after running for awhile and no pills, dispense is empty
         unsigned long waiting_time = (micros() - start_time)/1000;
         if(waiting_time >= MAX_WAITING_TIME) {
           Serial.println("!empty_compartment");
           servo.detach();
           return;
         }
       }
       DEBUG_OUT("Pill detected!*********************");
       
       ++pills_dispensed;
       start_time = micros();
       //back servo up
       servo.write(SERVO_BACKWARD);
       while(micros() - start_time < SERVO_REVERSE_TIME) {
         //keep checking phototransistor in case pills drop through by accident
         if(checkPhototransistor(compartments[index].detector)) {
           ++pills_dispensed;
           DEBUG_OUT("Pill detected (while backing up)!*******************");
         }
       }
       
       DEBUG_OUT("Stopping servo...\n");
       servo.write(SERVO_STOP);
     }
     servo.detach();
     
     //pause to let pills drop
     delay(1000);
     DEBUG_OUT("\nWeighing...");
     //weigh tray
     int tray_after = weighTray();
     
     int actual_pills_dispensed = calculatePillsDispensed(tray_before, tray_after, pill_weight); //calculate correct number of pills dispensed
     pills_in_tray += actual_pills_dispensed;
     total_pills_dispensed += actual_pills_dispensed;

     #ifdef _DEBUG
       Serial.print("Pill counts: ");
       Serial.print(pills_in_tray);
       Serial.print(" (in tray), ");
       Serial.print(total_pills_dispensed);
       Serial.println(" (dispensed total)");
     #endif
     if(pills_dispensed > num_pills) {
       DEBUG_OUT("Dumping...");
       dumpTrayContentsIntoTrash();
       pills_in_tray = 0;
     }
   }
   
   DEBUG_OUT("Dumping into cup...");
   dumpTrayContentsIntoCup();
   
   //turn laser off
   digitalWrite(compartments[index].diode, LOW);
   
   DEBUG_OUT("Done\n\n");
   
   //output dispensing stats
   Serial.println("!successful_dispense");
   Serial.println(total_pills_dispensed);
   delay(1000);*/
}
/*************************************/
bool pill_passing_through = false;
int no_light_threshold = 0;
int light_threshold = 0;
void setNoLightThreshold(int pin) {
  //TODO
  no_light_threshold = BLOCKED_LASER_THRESH;//readPhototransistor(pin);
}
void setLightThreshold(int pin) {
  //TODO
  light_threshold = UNBLOCKED_LASER_THRESH;//readPhototransistor(pin);
}
//return false is there is no pill detected
bool checkPhototransistor(int pin) {
   int val = readPhototransistor(pin);
   if(val < no_light_threshold) {
     if(!pill_passing_through) {
       pill_passing_through = true;
       return true;
     }
   }
   //hysteresis to detect multiple pills passing through
   if(val > light_threshold)
     pill_passing_through = false;
   return false;
}
int readPhototransistor(int pin) {
  /*int s = 0;
  for(int i = 0; i < NUM_PHOTO_SAMPLES; ++i) {
    s += analogRead(pin);
  }
  s /= NUM_PHOTO_SAMPLES;
  return s;*/
  return analogRead(pin);
}
bool isCupPresent() {
  return true;
}
/*************************************/
Servo tray;
int weighTray() {
  int res = -1;
  //keep reading until tray is stable
  while((res = trueRead()) == -1)
    ;
  return res;
}

#define LEN 1000
int trueRead() {
  long s = 0;
  int last_read = analogRead(PIN_TRAY);
  for(int i = 0; i < LEN; ++i) {
    int this_read = analogRead(PIN_TRAY);
    //if tray is unstable, cancel the read
    if(abs(this_read - last_read) > 5) {
      DEBUG_OUT("jitter");
      delay(100);
      return -1;
    }
    last_read = this_read;
    s += this_read;
  }
  return s/LEN;
}
#undef LEN

void dumpTrayContentsIntoCup() {
  tray.attach(PIN_TRAY_SERVO);
  delay(1000);
  tray.detach();

}
void dumpTrayContentsIntoTrash() {
  tray.attach(PIN_TRAY_SERVO);
  delay(1000);
  tray.detach();
}
int calculatePillsDispensed(int tray_before, int tray_after, int pill_weight) {
  double per_pill_weight = .03 * pill_weight;
  double diff = tray_after - tray_before;
  //diff *= MG_PER_MV * 5000.0 / 1024;
  diff /= per_pill_weight;
  return round(diff);
}
