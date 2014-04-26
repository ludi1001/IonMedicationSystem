import web
import json

urls = (
  '/', 'index',
  '/notification/pack/check', 'check_notification', #checks to see if there are any notifications
  '/notification/pack/confirm', 'confirm_notification', #confirms that the notifications were received
  '/ping', 'ping', #for testing purposes
  '/dispense', 'dispense' , #dispense medication
  '/status', 'status', #check dispensing status
)

if __name__ == "__main__":
  app = web.application(urls, locals())
  app.run()

    
class index:
  def GET(self):
    return "Hello, world!"
    
  def POST(self):
    input = web.input()
    data = web.data()
    print ("data: " + data)
    print (input)
    return "Hi " + input.name

class check_notification:
  def GET(self):
    return "1"
    
class confirm_notification:
  def GET(self):
    return "1"

class JSONAction(object):
  def response(self, input):
    return {}  
    
  def GET(self):
    input = web.input()
    web.header('Content-Type', 'application/javascript')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    res = self.response(input)
    r = input.callback + '(' + json.dumps(res) + ')'
    print r
    return r
    
  def OPTIONS(self):
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    web.header('Access-Control-Allow-Headers',  'X-Requested-With')
    return
  
class ping(JSONAction):
  def response(self, input):
    return input.data

dispenser = Dispenser()

#constructs json response from dispenser object
def parse_dispenser_status(dispenser):
  res = {}
  status = dispenser.get_status()
  res["status"] = status
  if status == Dispenser.ERROR:
    res["message"] = dispenser.get_error_message()
  elif status == Dispenser.IDLE:
    res["feedback"] = dispenser.get_feedback()
  return res

class dispense(JSONAction):
  def response(self, input):
    global dispenser
    data = json.loads(input)
    dispenser.dispense(data)
    return parse_dispenser_status(dispenser)

class status(JSONAction):
  def response(self, input):
    return parse_dispenser_status(dispenser)
    