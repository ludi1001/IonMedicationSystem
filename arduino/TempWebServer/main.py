import web
import json

urls = (
	'/', 'index',
	'/notification/pack/check', 'check_notification', #checks to see if there are any notifications
  '/notification/pack/confirm', 'confirm_notification' #confirms that the notifications were received
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