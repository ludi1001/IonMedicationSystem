#include <Process.h>

#define PIN_BATTERY_LOW  8
#define PIN_DISCONNECTED 13
#define PIN_MOTOR        9
#define PIN_SPEAKER      10

#define PIN_DISMISS       7
#define INTERRUPT_DISMISS 4

#define CYCLE_TIME                250 //run loop every 250 ms
#define LOW_BATTERY_VCC           4600 //low battery indicator
#define CONNECTED_CURL_COUNT      1200 //number of cycles to wait before checking for notifications if connected to server
#define DISCONNECTED_CURL_COUNT   240 //number of cycles to wait before checking for notifications if disconnected

void setup() {
  // Initialize Bridge
  Bridge.begin();
  
  Serial.begin(9600);
  
  pinMode(PIN_DISMISS, INPUT_PULLUP);
  attachInterrupt(INTERRUPT_DISMISS, dismiss, LOW);
  
  pinMode(PIN_BATTERY_LOW, OUTPUT);
  pinMode(PIN_DISCONNECTED, OUTPUT);
  notifySetup();
}

int loop_count = 0;
void loop() {
  //check battery
  checkBatteryStatus();
  
  //do anything that notification may want to do
  notifyLoop();
  
  //check for notifications
  curlLoop();
  delay(CYCLE_TIME);
}

/*==========================================================================*/
bool notification_on = false;
bool speaker_on = false;
void notifySetup() {
  pinMode(PIN_MOTOR, OUTPUT);
  pinMode(PIN_SPEAKER, OUTPUT);
}

void notify() {
  notification_on = true;
  speaker_on = true;
  digitalWrite(PIN_MOTOR, HIGH);
  digitalWrite(PIN_SPEAKER, HIGH);
}

void notifyLoop() {
  if(!notification_on) return;
  
  //turn sound on and off
  speaker_on = !speaker_on;
  if(speaker_on) digitalWrite(PIN_SPEAKER, HIGH);
  else digitalWrite(PIN_SPEAKER, LOW);
}

void stopNotify() {
  notification_on = false;
  speaker_on = false;
  digitalWrite(PIN_MOTOR, LOW);
  digitalWrite(PIN_SPEAKER, LOW);
}

void dismiss() {
  delay(800);
  if(digitalRead(PIN_DISMISS) == LOW) {
    //real dismissal
    stopNotify();
  }
}
/*==============================================================================*/
int curl_loop_count = 0;
bool disconnected = false;
void curlLoop() {
  int count = disconnected ? DISCONNECTED_CURL_COUNT : CONNECTED_CURL_COUNT;
  if(curl_loop_count >= count) {
    runCurl();
    curl_loop_count = 0;
  }
  
  //output connection status
  if(disconnected)
    digitalWrite(PIN_DISCONNECTED, HIGH);
  else
    digitalWrite(PIN_DISCONNECTED, LOW);
}

void runCurl() {
  Process p;        // Create a process and call it "p"
  p.begin("curl");  // Process that launch the "curl" command
  p.addParameter("http://10.190.87.162/notification/pack/check"); // Add the URL parameter to "curl"
  p.addParameter("--connect-timeout");
  p.addParameter("5");
  p.run();      // Run the process and wait for its termination

  // Print arduino logo over the Serial
  // A process output can be read with the stream methods
  if (p.available()>0) {
    char c = p.read();
    if(c == '1') {
      //we have a notification!
      disconnected = false;
      confirmReceivedNotification();
      notify();
    }
    else if(c == '0') {
      disconnected = false;
    }
    else {
      //it's not no notification either... something's messed up
      disconnected = true;
    }
  }
  else {
    disconnected = true; //error
  }
}

void confirmReceivedNotification() {
  Process p;
  p.begin("curl");
  p.addParameter("http://10.190.87.162/notification/pack/confirm");
  p.run();
}
/*===========================================================================*/

void checkBatteryStatus() {
  if(readVcc() < LOW_BATTERY_VCC) {
    digitalWrite(PIN_BATTERY_LOW, HIGH);
  }
  else {
    digitalWrite(PIN_BATTERY_LOW, LOW);
  }
}

/*readVcc() code from http://www.instructables.com/id/Secret-Arduino-Voltmeter/*/
long readVcc() {
  // Read 1.1V reference against AVcc
  // set the reference to Vcc and the measurement to the internal 1.1V reference
  #if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
     ADMUX = _BV(MUX5) | _BV(MUX0) ;
  #else
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #endif  
 
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Start conversion
  while (bit_is_set(ADCSRA,ADSC)); // measuring
 
  uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH  
  uint8_t high = ADCH; // unlocks both
 
  long result = (high<<8) | low;
 
  result = 1125300L / result; // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
  return result; // Vcc in millivolts
}
