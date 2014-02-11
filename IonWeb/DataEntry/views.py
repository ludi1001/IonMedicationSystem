from django.shortcuts import render_to_response
from django.template import RequestContext
from models import patient
from helper import RxNorm
import datetime
import urllib2
import json

# a lot of this was taken from a sample 'blongo' project
def patientinfo(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newPatient':
         name = request.POST['name']
         newPatient = patient(name=name)
         newPatient.save()

      if request.POST['requestType'] == 'deletePatient':
         id = request.POST['id']
         patient.objects(id=id)[0].delete()
         # don't know if we actually want to give people the ability to delete medical records...

   return render_to_response('patientinfo.html', {'Patients': patient.objects},
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
   
def medinfo(request):
   if 'requestType' in request.GET:
      if request.GET['requestType'] == 'getNameSuggestions':
         name = request.GET['medName']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/spellingsuggestions?name=', name])
         nameSuggestions = RxNorm.getJSON(url)
         return render_to_response('medinfo.html', {'nameSuggestions': nameSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedSuggestions':
         name = request.GET['medName']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/drugs?name=', name])
         medSuggestions = RxNorm.getJSON(url)
         return render_to_response('medinfo.html', {'medSuggestions': medSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedicationInfo':
         medID = request.GET['medID']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', medID])
         attributes = RxNorm.getJSON(''.join([url, '/allProperties?prop=attributes']))
         names = RxNorm.getJSON(''.join([url, '/allProperties?prop=names']))
         ndcs = RxNorm.getJSON(''.join([url, '/ndcs']))
         ndc = ndcs['ndcGroup']['ndcList']['ndc'][0]
         name = RxNorm.getName(medID);
         # dailymed = RxNorm.getJSON(''.join(['http://dailymed.nlm.nih.gov/dailymed/services/v1/ndc/', ndc, '/imprintdata.json']))
         return render_to_response('medinfo.html', {'attributes': json.dumps(attributes, indent=3), 'names': names, 'ndc': ndc, 'rxuid': medID, 'name' : name}, 
         context_instance=RequestContext(request))
   
   return render_to_response('medinfo.html', {}, context_instance=RequestContext(request))

