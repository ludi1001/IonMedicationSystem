from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from models import Notification
from account.privilege_tests import *

import json
from datetime import datetime

#temporary function
def generate_notification(request):
  obj = json.loads(request.body)
  return HttpResponse("hi")
  # return render_to_response('index.html', {},
  #  context_instance=RequestContext(request))

#temporary  
def get_all_notifications(request):
  data = []
  for n in Notification.objects:
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
  json_list = [{'id':101, 'generator':"TestGenerator", 'last_modified':datetime.now().strftime(DATE_STRING_FORMAT)}]
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
    obj = json.loads(request.body)
    user = IonUser.objects(user=request.user)[0] #corrupt database if this crashes
    
    earliest = datetime.strptime(obj['earliest'], DATE_STRING_FORMAT)
    latest = datetime.strptime(obj['latest'], DATE_STRING_FORMAT)
    
    #query notifications
    notifications = Notification.objects(target=user,id__generation_time__gte=earliest,id__generation_time__lte=latest)
    json_list = [{'id':n.id,
                  'generator':n.generator, 
                  'last_modified':n.modified_date.strftime(DATE_STRING_FORMAT), 
                  'type':n.type} for n in notifications]
    
    #mark that notifications have been read
    for n in notifications:
      n.mark_read()
    
    return HttpResponse(json.dumps(json_list),mimetype='application/json')
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}',mimetype='application/json')
  
  
