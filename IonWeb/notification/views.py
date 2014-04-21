from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from account.privilege_tests import *

from DataEntry.models import patient
from models import notification
from account.models import IonUser
from helper import RxNorm, helper
from notify import runNotify

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
  latest:time,
  recent:number
  }
  
  Returns JSON list of notifications
  """
  DATE_STRING_FORMAT = '%m/%d/%Y %H:%M:%S'
  try:
    obj = json.loads(request.body)
    user = IonUser.objects(user=request.user)[0] #corrupt database if this crashes
    
    notifications = None
    #setup the filtering
    filter = {'target':user}
    if 'earliest' in obj: #notifications since earliest
      earliest = datetime.strptime(obj['earliest'], DATE_STRING_FORMAT)
      filter['creation_date__gte'] = earliest
    if 'latest' in obj: #notifications before latest
      latest = datetime.strptime(obj['latest'], DATE_STRING_FORMAT)
      filter['creation_date__lte'] = latest
    if 'recent' in obj: #find the most recent ones
      recent = obj['recent']

    #query notifications
    if 'recent' not in obj:
      notifications = notification.objects(**filter)
    else:
      notifications = notification.objects(**filter).order_by('-creation_date')[:recent]

    json_list = [{'id':str(n.id),
                  'generator':n.generator, 
                  'creation_date':n.creation_date.strftime(DATE_STRING_FORMAT),
                  'last_modified':n.modified_date.strftime(DATE_STRING_FORMAT), 
                  'unread': True if n.viewed_date is None else False,
                  'type':n.type} for n in notifications]

    #mark that notifications have been read
    #for n in notifications:
    #  n.mark_read()
      
    return HttpResponse(json.dumps(json_list),content_type='application/json')
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}',content_type='application/json')

@is_in_group(ALL)
def mark_notification_read(request):
  """Expects JSON request in the form
  {
  id:id
  }
  Marks notification with id id as read
  """
  try:
    obj = json.loads(request.body)
    if 'id' not in obj:
      return HttpResponse('{"error":"No id"}',content_type='application/json')
      
    user = IonUser.objects(user=request.user)[0] #corrupt database if this crashes
    notifications = notification.objects(id=obj["id"],target=user) #make sure only target user can mark notification as read
    if len(notifications) == 0:
      return HttpResponse('{"error":"Invalid id"}',content_type='application/json')
      
    notifications[0].mark_read()
    
    return HttpResponse('{"success":"success"}',content_type='application/json')
  except ValueError:
    return HttpResponse('{"error":"Malformed JSON"}',mimetype='application/json')

def medication_status(request):
   message = ''
   if request.method == 'POST':
      if request.POST['requestType'] == 'takeMed':
         rxuid = request.POST['rxuid']
         quantity = request.POST['quantity']
         patientID = request.POST['patientID']
         message = take_medication(patient.objects(id=patientID)[0], rxuid, quantity, "ONLINE")
         
   minusone = datetime.now()-timedelta(hours=1)
   now = datetime.now()
   plusone = datetime.now()+timedelta(hours=1)
   
   timeset = [ minusone.strftime("%I:00%p").lower(), now.strftime("%I:00%p").lower(), plusone.strftime("%I:00%p").lower() ]
   
   ActivePatients = helper.active_medications(timeset, 1)
   print ActivePatients
   medDict = {}
   
   # TODO: recheck medication taken history
   for active_patient in ActivePatients:
      medications = []
      for medication in active_patient.medications:
         if medication['rxuid'] in active_patient.activeMeds and any((True for x in medication['times'] if x in timeset)):
            medications.append(medication)
            
      if medications:
         medDict[active_patient] = medications;
   
   print ActivePatients
   return render_to_response('medStatus.html', {'medDict': medDict, 'time' : datetime.now().strftime("%I:00%p"), 'message' : message}, context_instance=RequestContext(request))

def take_medication(Patient, rxuid, quantity, dispenserID):
   medEntry = {}
   medEntry['rxuid'] = rxuid
   medEntry['quantity'] = quantity
   medEntry['timestamp'] = datetime.now()
   medEntry['dispenserID'] = dispenserID;
   
   Patient.medHistory.append({ 'MedicationTaken' : medEntry })
   Patient.activeMeds.remove( rxuid )
   Patient.save()
   # TODO: remove flag
   return Patient.firstName + " " + Patient.lastName + " took medication " + rxuid 
   
def notifications(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newNotification':
         notificationType = request.POST['notificationType']
         id = request.POST['userID']
         
         target = IonUser.objects(id=id)[0]
   
         newNotification = notification(target=target, type=notificationType, generator = "ONLINE")
         newNotification.save()
         
   return render_to_response('notifications.html', {'Notifications': notification.objects}, context_instance=RequestContext(request))

def notify(request):
   runNotify()

   return render_to_response('notifications.html', {'Notifications': notification.objects}, context_instance=RequestContext(request))

def notificationMessage(notein):
   if notein.type == 'reminder':
      patientName = notein.patientName
      medName = RxNorm.getName(notein.rxuid)
      time = notein.time
      return "Reminder for " + patientName + ": Take medication " + medName + " (" + time + ")"
   
   if notein.type == 'missed':
      patientName = notein.patientName
      name = RxNorm.getName(notein.rxuid)
      time = notein.time
      return patientName + " missed medication " + medName + " (" + time + ")"
   
   return "unknown notification type"