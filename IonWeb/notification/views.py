from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from account.privilege_tests import *

from DataEntry.models import patient
from models import notification
from account.models import IonUser

import json
from datetime import datetime, timedelta, date



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
    notifications = Notification.objects(target=user,id__generation_time__gte=earliest,id__generation_time__lte=latest)
    print notifications
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
  

def medication_status(request):
   minusone = datetime.now()-timedelta(hours=1)
   now = datetime.now()
   plusone = datetime.now()+timedelta(hours=1)
   
   timeset = [ minusone.strftime("%I:00%p").lower(), now.strftime("%I:00%p").lower(), plusone.strftime("%I:00%p").lower() ]
   
   ActivePatients = active_medications(timeset)
   
   return render_to_response('medStatus.html', {'ActivePatients': ActivePatients, 'time' : datetime.now().strftime("%I:00%p")}, context_instance=RequestContext(request))

   # if int flag is 0, return all valid and set flag to 1
   # if int flag is 1, return all valid with medflag still one
   # if int flag is 2, return all valid with medflag still one and set flag to 0
   
   # Returns patients with a medication that falls within a timeset range, whose start date is before or equal to today
   
def active_medications(timeset): 
   # medflag is set in cron script.

   # elemMatch ensures the matched elements occur in the same medication instance   
   ActivePatients = patient.objects(__raw__={ 'medications' : { '$elemMatch' : { 'times' : {'$in': timeset }, 'startDate' : { "$lte" : datetime.now().strftime("%Y-%m-%d") } } }})
   
   medDict = {};
   
   # check medication taken history
   for active_patient in ActivePatients:
      medications = [];
      for medication in active_patient.medications:
         for time in medication['times']:
            if time in timeset:
               print medication['rxuid']
               medications.append(medication);
         
      medDict[active_patient] = medications;

   return medDict

def notifications(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newNotification':
         notificationType = request.POST['notificationType']
         id = request.POST['userID']
         
         target = IonUser.objects(id=id)[0]
   
         newNotification = notification(target=target, type=notificationType, generator = "ONLINE")
         newNotification.save()
         
   return render_to_response('notifications.html', {'Notifications': notification.objects}, context_instance=RequestContext(request))
