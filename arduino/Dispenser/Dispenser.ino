#include <Servo.h>

#define NUM_COMPARTMENTS 6  //number of compartments
#define MAX_PILLS       10 //maximum number of pills to dispense
#define MAX_PILL_WEIGHT 1000 //max pill weight in mg

#define PIN_TRAY 1

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
  
  setupCompartments();
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
   //turn laser diode on
   //read phototransistor value
   
   int pills_dispensed = 0; //pills dispensed for patient
   int total_pills_dispensed = 0; //pills dispensed in total, including those trashed
   while(pills_dispensed < pill_weight) {
     
     //weight tray beforehand
     int tray_before = weighTray();

     
     //turn servo on
     Servo servo;
     servo.attach(compartments[index].servo);
     
     int pills_dispensed = 0;
     while(pills_dispensed < pill_weight) {
       //if after running for awhile and no pills, dispense is empty
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
   
   //output dispensing stats
   Serial.println(pills_dispensed);
   Serial.println(total_pills_dispensed);
}
/*************************************/
bool isCupPresent() {
  return true;
}
/*************************************/
Servo tray;
int weighTray() {
  
}
void dumpTrayContentsIntoCup() {
  tray.attach(PIN_TRAY);
  tray.detach();
}
void dumpTrayContentsIntoTrash() {
  tray.attach(PIN_TRAY);
  tray.detach();
}
int calculatePillsDispensed(int tray_before, int tray_after, int pill_weight) {
  double diff = tray_after - tray_before;
  diff /= pill_weight;
  return round(diff);
}
