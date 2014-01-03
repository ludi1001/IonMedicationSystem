from django.shortcuts import render_to_response
from django.template import RequestContext
from models import patient
import datetime

# a lot of this was taken from a sample 'blongo' project
def index(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newPatient':
         name = request.POST['name']
         newPatient = patient(name=name)
         newPatient.creationTime = datetime.datetime.now()
         newPatient.save()

      if request.POST['requestType'] == 'deletePatient':
         id = eval("request." + request.method + "['id']")
         patient.objects(id=id)[0].delete()
         # don't know if we actually want to give people the ability to delete medical records...

   return render_to_response('index.html', {'Patients': patient.objects},
                              context_instance=RequestContext(request))

def update(request):
   id = eval("request." + request.method + "['id']")
   Patient = patient.objects(id=id)[0]

   if request.method == 'POST':
      Patient.name = request.POST['name']
      Patient.editedTime = datetime.datetime.now()
      Patient.dispenserID = request.POST['dispenserID']
      Patient.save()
      template = 'index.html'
      params = {'Patients': patient.objects}

   elif request.method == 'GET':
      template = 'update.html'
      params = {'patient':Patient}

   return render_to_response(template, params, context_instance=RequestContext(request))