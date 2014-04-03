from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from account.privilege_tests import *

from DataEntry.models import patient
from models import notification
from account.models import IonUser

import json
from datetime import datetime, timedelta



#temporary function
def generate_notification(request):
  obj = json.loads(request.body)
  return HttpResponse("hi")
  # return render_to_response('index.html', {},
  #  context_instance=RequestContext(request))

#temporary  
def get_all_notifications(request):
  data = []
  for n in notification.objects:
    data.append({"generator": str(n.generator),
      "creation_date": str(n.creation_date),
      "modified_date": str(n.modified_date),
      "target": str(n.target.__id),
      "type": str(n.type)
    })
  return HttpResponse(json.dumps(data),mimetype='application/json')

#temporary
def get_dummy_notifications(request):
  DATE_STRING_FORMAT = '%m/%d/%Y %H:%M:%S'
  json_list = [{'id':101, 'generator':"TestGenerator", 'last_modified':datetime.now().strftime(DATE_STRING_FORMAT)},{'id':102, 'generator':"TestGenerator", 'last_modified':(datetime.now()+timedelta(hours=2)).strftime(DATE_STRING_FORMAT)},{'id':103, 'generator':"TestGenerator", 'last_modified':(datetime.now()+timedelta(minutes=3)).strftime(DATE_STRING_FORMAT)}]
  return HttpResponse(json.dumps(json_list),mimetype='application/json')

@is_in_group(ALL)
def get_notifications(request):
  """Expects JSON request in the form
  {
  earliest:time,
  latest:time
  }
  
  Returns JSON list of notifications
  """
  DATE_STRING_FORMAT = '%m/%d/%Y %H:%M:%S'
  try:
    print request.body
    obj = json.loads(request.body)
    user = IonUser.objects(user=request.user)[0] #corrupt database if this crashes
    
    earliest = datetime.strptime(obj['earliest'], DATE_STRING_FORMAT)
    latest = datetime.strptime(obj['latest'], DATE_STRING_FORMAT)

    #query notifications
    notifications = notification.objects(target=user,creation_date__gte=earliest,creation_date__lte=latest)

    json_list = [{'id':str(n.id),
                  'generator':n.generator, 
                  'creation_date':n.creation_date.strftime(DATE_STRING_FORMAT),
                  'last_modified':n.modified_date.strftime(DATE_STRING_FORMAT), 
                  'type':n.type} for n in notifications]

    #mark that notifications have been read
    for n in notifications:
      n.mark_read()
      
    return HttpResponse(json.dumps(json_list),content_type='application/json')
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}',content_type='application/json')
  
  
def notifications(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newNotification':
         notificationType = request.POST['notificationType']
         id = request.POST['userID']
         
         target = IonUser.objects(id=id)[0]
   
         newNotification = notification(target=target, type=notificationType, generator = "ONLINE")
         newNotification.save()
         
   return render_to_response('notifications.html', {'Notifications': notification.objects},
                              context_instance=RequestContext(request))
