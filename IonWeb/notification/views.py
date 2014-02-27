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
  
def get_notifications(request):
  try:
    obj = json.loads(request.body)
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}')
  
  
