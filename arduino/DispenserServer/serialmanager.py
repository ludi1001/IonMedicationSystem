import thread
import serial
import traceback

PORT = 'COM3'

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
        ser = serial.Serial(PORT, 9600, timeout=2)
          
        for key, value in data.items():
          #key contains container index, value contains number of pills
          ser.write('!dispense\n')
          ser.write(str(key) + '\n')
          ser.write(str(value) + '\n')
          
          result = ser.readline()
          res = {"compartment": key}
          
          if result == "!error":
            res["result"] = "error"
            res["value"] = ser.readline()
          elif result == "!empty_compartment":
            res["result"] = "empty"
          elif result == "!successful_dispense":
            res["result"] = "success"
            pills_dispensed = int(ser.readline())
            res["total_pills_dispensed"] = int(ser.readline())
          else:
            res["result"] = "unknown"
            res["value"] = result
          self.feedback.append(res)
        ser.close()
        self.status = Dispenser.IDLE
      except:
        self.status = Dispenser.ERROR
        self.error_msg = traceback.format_exc()
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
