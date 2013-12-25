from django.shortcuts import render_to_response
from django.template import RequestContext
from models import patient
import datetime

def index(request):
    if request.method == 'POST':
       # save new patient
       name = request.POST['name']
       newPatient = patient(name=name)
       newPatient.creationTime = datetime.datetime.now()
       newPatient.save()

    # Get all patients from DB
    patients = patient.objects 
    return render_to_response('index.html', {'Patients': patients},
                              context_instance=RequestContext(request))