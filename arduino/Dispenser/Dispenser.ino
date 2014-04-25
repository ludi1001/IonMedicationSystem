#include <Servo.h>

#define NUM_COMPARTMENTS  6  //number of compartments
#define MAX_PILLS         10 //maximum number of pills to dispense
#define MAX_PILL_WEIGHT   1000 //max pill weight in mg
#define MAX_WAITING_TIME  1000000 //max time (in microseconds) to wait for pill to dispense before concluding it is empty 
#define MG_PER_MV         2 //mg per mv for tray
#define NUM_PHOTO_SAMPLES 10 //number of samples to take for phototransistor readings

#define PIN_TRAY_SERVO 1
#define PIN_TRAY       2

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
  Serial.println("Starting up...");
  Serial.setTimeout(500);
  
  pinMode(PIN_TRAY, INPUT);
  
  setupCompartments();
  for(int i = 0; i < NUM_COMPARTMENTS; ++i) {
    pinMode(compartments[i].diode, OUTPUT);
    pinMode(compartments[i].detector, INPUT);
  }
}

void setupCompartments() {
}

void loop() {
  if(Serial.available()) {
    char first_char = Serial.read();

    char buffer[100];
    buffer[0] = 0;
    int res = Serial.readBytesUntil('\n', buffer, 100);
    if(res <= 0) return; //make sure we read nonzero data
    
    if(first_char == '!') { //a command was sent
      if(strcmp(buffer, "ping") == 0)
        ping();
      else if(strcmp(buffer, "dispense") == 0)
        dispense();
    }
    else {
      Serial.println(buffer); //echo back
    }
  }
}
/**************************************/
void ping() {
  Serial.println("ping successful");
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
     Serial.println("Bad number of pills");
     return;
   }
   
   //get pill weight
   int pill_weight = Serial.parseInt();
   if(pill_weight <= 0 || pill_weight >= MAX_PILL_WEIGHT) {
     Serial.println("!error");
     Serial.println("Bad pill weight");
   }
   
        
   //read ambient noise for phototransistor
   int phototransistor_no_light = readPhototransistor(compartments[index].detector);
   //turn laser diode on
   digitalWrite(compartments[index].diode, HIGH);
   //read phototransistor value
   int phototransistor_with_light = readPhototransistor(compartments[index].detector);
   
   int pills_dispensed = 0; //pills dispensed for patient
   int total_pills_dispensed = 0; //pills dispensed in total, including those trashed
   while(pills_dispensed < pill_weight) {
     
     //weight tray beforehand
     int tray_before = weighTray();
     
     //turn servo on
     Servo servo;
     servo.attach(compartments[index].servo);
     
     unsigned long start_time = micros();
     
     int pills_dispensed = 0;
     while(pills_dispensed < pill_weight) {
       if(true /*optical sensor detected something*/) {
         ++pills_dispensed;
         start_time = micros();
       }
       //if after running for awhile and no pills, dispense is empty
       unsigned long waiting_time = micros() - start_time;
       if(waiting_time >= MAX_WAITING_TIME) {
         Serial.println("!empty_compartment");
         return;
       }
     }
     
     //stop servo
     servo.detach();
     
     //weigh tray
     int tray_after = weighTray();
     
     pills_dispensed = calculatePillsDispensed(tray_before, tray_after, pill_weight); //calculate correct number of pills dispensed
     total_pills_dispensed += pills_dispensed;
     
     if(pills_dispensed == num_pills) {
       dumpTrayContentsIntoCup();
     }
     else {
       dumpTrayContentsIntoTrash();
     }
   }
   
   //turn laser off
   digitalWrite(compartments[index].diode, LOW);
   
   //output dispensing stats
   Serial.println("!successful_dispense");
   Serial.println(pills_dispensed);
   Serial.println(total_pills_dispensed);
}
/*************************************/
int readPhototransistor(int pin) {
  int s = 0;
  for(int i = 0; i < NUM_PHOTO_SAMPLES; ++i) {
    s += analogRead(pin);
  }
  s /= NUM_PHOTO_SAMPLES;
  return s;
}
bool isCupPresent() {
  return true;
}
/*************************************/
Servo tray;
int weighTray() {
  int val = analogRead(PIN_TRAY);
  return val;
}
void dumpTrayContentsIntoCup() {
  tray.attach(PIN_TRAY_SERVO);
  tray.detach();
}
void dumpTrayContentsIntoTrash() {
  tray.attach(PIN_TRAY_SERVO);
  tray.detach();
}
int calculatePillsDispensed(int tray_before, int tray_after, int pill_weight) {
  double diff = tray_after - tray_before;
  diff *= MG_PER_MV * 5000.0 / 1024;
  diff /= pill_weight;
  return round(diff);
}
