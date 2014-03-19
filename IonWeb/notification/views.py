from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from models import Notification

import json

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
  
def get_notifications(request):
  try:
    obj = json.loads(request.body)
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}',mimetype='application/json')
  
  
