import thread
import serial
import traceback
import time

PORT = 'COM5'

class Dispenser:
  IDLE = 0
  BUSY = 1
  ERROR = 2
  KILL = 3 #kill the dispense process
  DONE = 4
  
  def __init__(self):
    self.status = Dispenser.IDLE
    self.error_msg = ""
    self.feedback = []
    
  def dispense(self, data):
    def run_dispenser(data):
      self.status = Dispenser.BUSY
      self.feedback = []
      try:
        ser = serial.Serial(PORT, 9600)
        time.sleep(3)
        ser.write('!ping\n')
        print ser.readline()
        print data
        for entry in data['dispense']:
          print 'Processing entry...'
          print entry
          
          ser.flushInput() #clear input buffer so we know all data sent is from this command
          #key contains container index, value contains number of pills
          ser.write('!dispense\n')
          ser.write(str(entry['compartment']) + '\n')
          ser.write(str(entry['pills']) + '\n')
          ser.write(str(entry['weight']) + '\n')
          
          print 'Waiting for result...'
          
          result = ser.readline().strip()
          while not result:
            result = ser.readline().strip()
          res = {"compartment": entry["compartment"]}
          
          print 'Result: ' + result
          
          if result == "!error":
            res["result"] = "error"
            res["value"] = ser.readline().strip()
          elif result == "!empty_compartment":
            res["result"] = "empty"
          elif result == "!successful_dispense":
            res["result"] = "success"
            res["total_pills_dispensed"] = int(ser.readline().strip())
          else:
            res["result"] = "unknown"
            res["value"] = result
          self.feedback.append(res)
        ser.close()
        self.status = Dispenser.IDLE
      except:
        self.status = Dispenser.ERROR
        self.error_msg = traceback.format_exc()
    
    if self.status != Dispenser.BUSY:
      self.status = Dispenser.BUSY
      try:
        thread.start_new_thread(run_dispenser, (data, ))
      except:
        self.status = Dispenser.ERROR
        self.error_msg = "Unable start thread"
  
  def get_status(self):
    return self.status
    
  def get_error_message(self):
    return self.error_msg
    
  def get_feedback(self):
    return self.feedback
    
  def clear_feedback(self):
    self.feedback = []
